import hou
import os
import re
from PySide6 import QtCore, QtGui, QtWidgets

# ========================== Drag/parse helpers ==========================

def _strip_wrappers(text: str) -> str:
    """Remove wrappers like ch(), chs(), chf() around quoted parm refs; accept op:/ scheme."""
    text = text.strip()
    m = re.match(r'^[a-zA-Z_]+\s*\(\s*"(.*)"\s*\)\s*$', text)
    if m:
        return m.group(1)
    m = re.match(r"^[a-zA-Z_]+\s*\(\s*'(.*)'\s*\)\s*$", text)
    if m:
        return m.group(1)
    if text.startswith("op:"):
        return text[3:]
    return text

def _extract_parm_from_text(raw: str):
    """
    Parse many likely forms and return (node_path, parm_name) or (None, None).
    /path/node.parm      -> ('/path/node', 'parm')
    /path/node/parm      -> ('/path/node', 'parm')
    ch("/path/node/parm")-> ('/path/node', 'parm')
    ../parm              -> (resolved_node_path, 'parm') if selection exists
    rough                -> (None, 'rough')
    """
    s = _strip_wrappers(raw).strip()

    if s.startswith("/") and "." in s:
        node_path, parm_name = s.rsplit(".", 1)
        return node_path, parm_name

    if s.startswith("/"):
        parts = s.split("/")
        if len(parts) >= 3:
            node_path = "/".join(parts[:-1])
            parm_name = parts[-1]
            return node_path, parm_name

    if s and "/" in s and not s.startswith("/"):
        sel = hou.selectedNodes()
        base = sel[0] if sel else None
        if base is not None:
            try:
                abs_path = f"{base.path()}/{s}"
                norm = os.path.normpath(abs_path).replace("\\", "/")
                node_path = os.path.dirname(norm)
                parm_name = os.path.basename(norm)
                return node_path, parm_name
            except Exception:
                pass

    if s and "/" not in s and "." not in s:
        return None, s

    return None, None

def _iter_all_nodes():
    root = hou.node("/")
    stack = [root]
    while stack:
        n = stack.pop()
        yield n
        try:
            stack.extend(n.children())
        except Exception:
            pass

def _iter_descendants(start_node: hou.Node):
    stack = list(start_node.children())
    while stack:
        n = stack.pop()
        yield n
        try:
            stack.extend(n.children())
        except Exception:
            pass

def _coerce_value(parm_or_first_of_tuple, text: str):
    """
    Coerce text into a sensible value: bool words -> 0/1, int/float if numeric, else string.
    Tuple broadcasting is handled by the caller.
    """
    s = text.strip()
    low = s.lower()
    if low in {"true", "on"}:
        v = 1
    elif low in {"false", "off"}:
        v = 0
    else:
        try:
            if re.fullmatch(r"[+-]?\d+", s):
                v = int(s)
            else:
                v = float(s)
        except Exception:
            v = s
    return v

def _html_escape(s: str) -> str:
    return (s.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))

# ========================== Robust drop-enabled line edit ==========================

class ParmDropLineEdit(QtWidgets.QLineEdit):
    """
    A QLineEdit that robustly accepts drags from Houdini (parm labels, nodes, etc.)
    and calls the provided callback with (node_path, parm_name).
    """
    def __init__(self, on_drop=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
        self._on_drop = on_drop
        self._log_mimes = False

    def setLogMimes(self, enabled: bool):
        self._log_mimes = bool(enabled)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        event.acceptProposedAction()

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent):
        event.acceptProposedAction()

    def dropEvent(self, event: QtGui.QDropEvent):
        md = event.mimeData()
        if self._log_mimes:
            print("DROP MIME FORMATS:", md.formats())

        text = ""
        if md.hasText():
            text = md.text().strip()
        if not text and md.hasUrls():
            urls = md.urls()
            if urls:
                text = urls[0].toString().strip()
        if not text:
            for fmt in md.formats():
                try:
                    raw = bytes(md.data(fmt)).decode(errors="ignore").strip()
                except Exception:
                    continue
                if raw and len(raw) < 8192:
                    text = raw
                    break
        if not text:
            cb = QtWidgets.QApplication.clipboard().text().strip()
            if cb:
                text = cb
        if not text:
            event.acceptProposedAction()
            return

        node_path, parm_name = _extract_parm_from_text(text)
        if self._on_drop:
            self._on_drop(node_path, parm_name)
        event.acceptProposedAction()

# ========================== Parameter list widget (DnD) ==========================

class ParmListTable(QtWidgets.QTableWidget):
    """
    Holds many (Parm, Value) rows.
    - Drop parm labels anywhere on it to append rows (auto-fill value if resolvable).
    - Value column is editable; Parm column is read-only.
    - Last column has ❌ buttons to remove a row.
    """
    rowAdded = QtCore.Signal()
    rowRemoved = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(0, 3, parent)
        self.setHorizontalHeaderLabels(["Parm", "Value", ""])
        self.horizontalHeader().setStretchLastSection(False)
        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.setColumnWidth(1, 260)
        self.setColumnWidth(2, 36)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setAcceptDrops(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DropOnly)
        self.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked | QtWidgets.QAbstractItemView.SelectedClicked | QtWidgets.QAbstractItemView.EditKeyPressed)

    def add_parm_row(self, parm_name: str, value: str = ""):
        if not parm_name:
            return
        # If parm already exists, update its value instead of duplicating
        for r in range(self.rowCount()):
            if self.item(r, 0) and self.item(r, 0).text() == parm_name:
                self.item(r, 1).setText(value)
                return

        r = self.rowCount()
        self.insertRow(r)

        parm_item = QtWidgets.QTableWidgetItem(parm_name)
        parm_item.setFlags(parm_item.flags() & ~QtCore.Qt.ItemIsEditable)
        self.setItem(r, 0, parm_item)

        value_item = QtWidgets.QTableWidgetItem(value)
        self.setItem(r, 1, value_item)

        btn = QtWidgets.QPushButton("DELETE")
        btn.setFixedWidth(28)
        btn.clicked.connect(lambda _=None, row=r: self._remove_row(row))
        self.setCellWidget(r, 2, btn)
        self.rowAdded.emit()

    def _remove_row(self, row: int):
        if 0 <= row < self.rowCount():
            self.removeRow(row)
            self.rowRemoved.emit()

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        event.acceptProposedAction()

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent):
        event.acceptProposedAction()

    def dropEvent(self, event: QtGui.QDropEvent):
        md = event.mimeData()

        texts = []
        if md.hasText():
            texts = [t.strip() for t in md.text().splitlines() if t.strip()]
        else:
            if md.hasUrls():
                for u in md.urls():
                    texts.append(u.toString().strip())
            if not texts:
                for fmt in md.formats():
                    try:
                        raw = bytes(md.data(fmt)).decode(errors="ignore")
                    except Exception:
                        continue
                    for chunk in re.split(r'[\r\n]+', raw):
                        t = chunk.strip()
                        if t:
                            texts.append(t)

        if not texts:
            cb = QtWidgets.QApplication.clipboard().text()
            if cb:
                texts = [t.strip() for t in cb.splitlines() if t.strip()]

        seen = set()
        for t in texts:
            node_path, parm_name = _extract_parm_from_text(t)
            if not parm_name:
                continue
            key = parm_name
            if key in seen:
                continue
            seen.add(key)

            value_str = ""
            if node_path:
                n = hou.node(node_path)
                if n:
                    p = n.parm(parm_name) or (n.parmTuple(parm_name)[0] if n.parmTuple(parm_name) else None)
                    if p:
                        try:
                            v = p.eval()
                            value_str = " ".join(map(str, v)) if isinstance(v, (list, tuple)) else str(v)
                        except Exception:
                            pass

            self.add_parm_row(parm_name, value_str)

        event.acceptProposedAction()

    def get_parms(self):
        """Return list of (parm_name, value_text)."""
        out = []
        for r in range(self.rowCount()):
            name_item = self.item(r, 0)
            value_item = self.item(r, 1)
            if not name_item:
                continue
            name = name_item.text().strip()
            value = value_item.text().strip() if value_item else ""
            if name:
                out.append((name, value))
        return out

# ========================== Main UI ==========================

class NodeBatchSetterUI(QtWidgets.QMainWindow):
    """
    Reference-driven search: infer category & node type from the Reference Node.
    Search same type in chosen scope (siblings / descendants / whole scene),
    optional name filter. Parameter list ONLY drives 'Has All Parms?' and apply gating.
    Includes an Update Summary panel after applying changes.
    """
    def __init__(self):
        super().__init__()
        self.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)
        self.setWindowTitle("Node Batch Setter")
        self.resize(1200, 820)

        self._ref_node = None
        self._matches = []          # [(hou.Node, has_all_parms_bool)]
        self._row_nodepath = {}     # row -> node.path()

        cw = QtWidgets.QWidget()
        self.setCentralWidget(cw)
        main = QtWidgets.QVBoxLayout(cw)

        # -------- Reference node row --------
        ref_row = QtWidgets.QHBoxLayout()
        self.ref_le = QtWidgets.QLineEdit()
        self.ref_le.setPlaceholderText("Drop or type a reference node path (e.g. /mat/glass_shader)")
        self.ref_le.setAcceptDrops(True)
        self.ref_le.installEventFilter(self)
        pick_btn = QtWidgets.QPushButton("Pick…")
        pick_btn.clicked.connect(self._pick_node)
        self.info_lbl = QtWidgets.QLabel("")
        self.info_lbl.setStyleSheet("color: #888;")
        ref_row.addWidget(QtWidgets.QLabel("Reference Node:"))
        ref_row.addWidget(self.ref_le, 1)
        ref_row.addWidget(pick_btn)
        ref_row.addWidget(self.info_lbl, 1)
        main.addLayout(ref_row)

        # -------- Scope + filter --------
        opts = QtWidgets.QHBoxLayout()
        self.scope_combo = QtWidgets.QComboBox()
        self.scope_combo.addItems([
            "Same network (siblings of reference)",
            "Under reference (descendants)",
            "Whole scene"
        ])
        self.name_contains = QtWidgets.QLineEdit()
        self.name_contains.setPlaceholderText("optional: name contains…")
        opts.addWidget(QtWidgets.QLabel("Scope:"))
        opts.addWidget(self.scope_combo, 1)
        opts.addWidget(QtWidgets.QLabel("Filter:"))
        opts.addWidget(self.name_contains, 1)
        main.addLayout(opts)

        # -------- Parameter list builder --------
        panel = QtWidgets.QGroupBox("Parameters to Set (drop parms here to add rows)")
        panel_l = QtWidgets.QVBoxLayout(panel)

        add_row = QtWidgets.QHBoxLayout()
        self.single_parm = ParmDropLineEdit(on_drop=self._fill_single_from_drop)
        self.single_parm.setPlaceholderText("Parm name (e.g. transmission, inputs:transmission)")
        self.single_value = ParmDropLineEdit(on_drop=self._fill_value_from_drop)
        self.single_value.setPlaceholderText("Value (e.g. 1, 0.5, true, 0 0 0, or string)")
        add_btn = QtWidgets.QPushButton("Add")
        add_btn.clicked.connect(self._add_single_parm)
        add_row.addWidget(self.single_parm, 1)
        add_row.addWidget(self.single_value, 1)
        add_row.addWidget(add_btn)
        panel_l.addLayout(add_row)

        self.parm_table = ParmListTable()
        panel_l.addWidget(self.parm_table)

        self.parm_table.rowAdded.connect(self._refresh_has_column)
        self.parm_table.rowRemoved.connect(self._refresh_has_column)

        main.addWidget(panel)

        # -------- Find & Nodes table --------
        find_row = QtWidgets.QHBoxLayout()
        find_btn = QtWidgets.QPushButton("Find Nodes")
        find_btn.clicked.connect(self._find_matches)
        self.count_lbl = QtWidgets.QLabel("0 matches (0 selected)")
        find_row.addWidget(find_btn)
        find_row.addStretch(1)
        find_row.addWidget(self.count_lbl)
        main.addLayout(find_row)

        self.table = QtWidgets.QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Node Name", "Path", "Type", "Has All Parms?"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self._update_selection_count)
        self.table.itemDoubleClicked.connect(self._on_table_double_click)
        main.addWidget(self.table, 1)

        # -------- Bottom actions --------
        actions = QtWidgets.QHBoxLayout()
        apply_btn = QtWidgets.QPushButton("Apply to Selected Rows (only nodes that have all parms)")
        apply_btn.clicked.connect(self._apply_to_selected_with_condition)
        actions.addStretch(1)
        actions.addWidget(apply_btn)
        main.addLayout(actions)

        # -------- Update Summary panel --------
        self.summary_group = QtWidgets.QGroupBox("Update Summary")
        self.summary_group.setCheckable(True)
        self.summary_group.setChecked(True)
        self.summary_text = QtWidgets.QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMinimumHeight(150)
        sg_layout = QtWidgets.QVBoxLayout(self.summary_group)
        sg_layout.addWidget(self.summary_text)
        main.addWidget(self.summary_group)

        # -------- Help --------
        help_lbl = QtWidgets.QLabel(
            "Drop/pick a reference node. Search finds SAME TYPE in chosen scope. "
            "Parm list does not filter search; it only sets the 'Has All Parms?' condition and apply gating."
        )
        help_lbl.setStyleSheet("color:#888;")
        main.addWidget(help_lbl)

        self.ref_le.textEdited.connect(self._refresh_ref_info)

    # ---------------- Event filter (reference field only) ----------------

    def eventFilter(self, obj, event):
        if obj is self.ref_le and event.type() == QtCore.QEvent.DragEnter:
            event.acceptProposedAction()
            return True
        if obj is self.ref_le and event.type() == QtCore.QEvent.Drop:
            md = event.mimeData()
            text = ""
            if md.hasText():
                text = md.text().strip()
            if not text and md.hasUrls():
                urls = md.urls()
                if urls:
                    text = urls[0].toString().strip()
            if text.startswith("op:"):
                text = text[3:]
            if "." in text and text.startswith("/"):
                text = text.rsplit(".", 1)[0]
            self.ref_le.setText(text)
            self._refresh_ref_info()
            event.acceptProposedAction()
            return True
        return super().eventFilter(obj, event)

    # ---------------- Parameter list helpers ----------------

    def _fill_single_from_drop(self, node_path, parm_name):
        if parm_name:
            self.single_parm.setText(parm_name)
            if node_path:
                n = hou.node(node_path)
                if n:
                    p = n.parm(parm_name) or (n.parmTuple(parm_name)[0] if n.parmTuple(parm_name) else None)
                    if p:
                        try:
                            v = p.eval()
                            self.single_value.setText(" ".join(map(str, v)) if isinstance(v, (list, tuple)) else str(v))
                        except Exception:
                            pass

    def _fill_value_from_drop(self, node_path, parm_name):
        if node_path and parm_name:
            n = hou.node(node_path)
            if n:
                p = n.parm(parm_name) or (n.parmTuple(parm_name)[0] if n.parmTuple(parm_name) else None)
                if p:
                    try:
                        v = p.eval()
                        self.single_value.setText(" ".join(map(str, v)) if isinstance(v, (list, tuple)) else str(v))
                    except Exception:
                        pass

    def _add_single_parm(self):
        name = self.single_parm.text().strip()
        val = self.single_value.text().strip()
        if not name:
            hou.ui.displayMessage("Enter a parameter name before adding.",
                                  severity=hou.severityType.Warning)
            return
        self.parm_table.add_parm_row(name, val)
        self._refresh_has_column()

    # ---------------- Search & results ----------------

    def _collect_candidates(self):
        """Collect nodes according to scope."""
        if not self._ref_node:
            return []

        scope = self.scope_combo.currentIndex()
        if scope == 0:  # siblings
            parent = self._ref_node.parent()
            return parent.children() if parent else []
        elif scope == 1:  # descendants
            return list(_iter_descendants(self._ref_node))
        else:  # whole scene
            return list(_iter_all_nodes())

    def _node_has_all_parms(self, node: hou.Node, parm_names):
        for name in parm_names:
            if node.parm(name):
                continue
            base = name.split(".")[0]
            if node.parmTuple(base) is not None:
                continue
            return False
        return True

    def _find_matches(self):
        self.table.setRowCount(0)
        self._matches.clear()
        self._row_nodepath.clear()

        # Require a reference node (source of type)
        if not self._ref_node:
            hou.ui.displayMessage("Pick or drop a Reference Node first.",
                                  severity=hou.severityType.Warning)
            return

        ref_type_name = self._ref_node.type().name()
        name_sub = self.name_contains.text().strip().lower()
        parm_names = [n for (n, _v) in self.parm_table.get_parms()]

        for n in self._collect_candidates():
            try:
                nt = n.type()
                if not nt or nt.name() != ref_type_name:
                    continue
                if name_sub and name_sub not in n.name().lower():
                    continue
            except Exception:
                continue

            has_all = self._node_has_all_parms(n, parm_names) if parm_names else True
            self._matches.append((n, has_all))

            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QtWidgets.QTableWidgetItem(n.name()))
            self.table.setItem(r, 1, QtWidgets.QTableWidgetItem(n.path()))
            self.table.setItem(r, 2, QtWidgets.QTableWidgetItem(n.type().name()))
            has_item = QtWidgets.QTableWidgetItem("Yes" if has_all else "No")
            if not has_all:
                has_item.setForeground(QtGui.QBrush(QtGui.QColor(200, 50, 50)))
            self.table.setItem(r, 3, has_item)
            self._row_nodepath[r] = n.path()

        self._update_selection_count()

    def _refresh_has_column(self):
        """Recompute 'Has All Parms?' when the parm list changes."""
        parm_names = [n for (n, _v) in self.parm_table.get_parms()]
        for r in range(self.table.rowCount()):
            node_path = self._row_nodepath.get(r)
            n = hou.node(node_path) if node_path else None
            has_all = True
            if n and parm_names:
                has_all = self._node_has_all_parms(n, parm_names)
            item = QtWidgets.QTableWidgetItem("Yes" if has_all else "No")
            if not has_all:
                item.setForeground(QtGui.QBrush(QtGui.QColor(200, 50, 50)))
            self.table.setItem(r, 3, item)
        self._update_selection_count()

    def _selected_nodes(self):
        rows = {i.row() for i in self.table.selectedIndexes()}
        result = []
        for r in sorted(rows):
            node_path = self._row_nodepath.get(r)
            if node_path:
                n = hou.node(node_path)
                if n:
                    result.append((r, n))
        return result

    def _update_selection_count(self):
        total = self.table.rowCount()
        selected = len({i.row() for i in self.table.selectedIndexes()})
        self.count_lbl.setText(f"{total} matches ({selected} selected)")

    def _on_table_double_click(self, item: QtWidgets.QTableWidgetItem):
        try:
            row = item.row()
            node_path = self._row_nodepath.get(row)
            if not node_path:
                return
            node = hou.node(node_path)
            if not node:
                hou.ui.displayMessage(f"Node not found anymore: {node_path}",
                                      severity=hou.severityType.Warning)
                return

            # Select it in Houdini and navigate the Network Editor there
            hou.clearAllSelected()
            node.setSelected(True)

            net_pane = None
            for pane in hou.ui.paneTabs():
                if isinstance(pane, hou.NetworkEditor):
                    net_pane = pane
                    break

            if net_pane:
                parent_path = node.parent().path() if node.parent() else node.path()
                net_pane.cd(parent_path)
                # Ensure our node is visible and focused
                net_pane.frameSelection()
            else:
                hou.ui.displayMessage("No Network Editor pane found to navigate.",
                                      severity=hou.severityType.Warning)
        except Exception as e:
            hou.ui.displayMessage(f"Failed to navigate: {e}",
                                  severity=hou.severityType.Error)

    # ---------------- Apply (only if node has all parms) ----------------

    def _apply_to_selected_with_condition(self):
        selected = self._selected_nodes()
        if not selected:
            hou.ui.displayMessage("Select at least one row in the nodes table.",
                                  severity=hou.severityType.Warning)
            return

        parm_items = self.parm_table.get_parms()
        if not parm_items:
            hou.ui.displayMessage("Add at least one parameter to the list.",
                                  severity=hou.severityType.Warning)
            return

        # Tally & per-node details for summary
        per_param_tally = {name: 0 for (name, _v) in parm_items}
        per_node_updates = {}  # node_path -> [(parm_name, value_text)]

        total_set = 0
        total_skipped_missing_condition = 0
        total_missing = 0
        total_failed = 0

        with hou.undos.group("Batch Set Multiple Parms (Has-All condition)"):
            for (row_idx, n) in selected:
                # Gate: only update if node has all parms
                if not self._node_has_all_parms(n, [pn for (pn, _v) in parm_items]):
                    total_skipped_missing_condition += 1
                    continue

                node_applied = []

                for (parm_name, value_text) in parm_items:
                    p = n.parm(parm_name)
                    tp = None
                    if not p:
                        base = parm_name.split(".")[0]
                        tp = n.parmTuple(base)
                        if not tp:
                            total_missing += 1
                            continue
                    try:
                        parts = value_text.split()
                        if tp and len(parts) == len(tp):
                            try:
                                vals = [
                                    (int(x) if re.fullmatch(r"[+-]?\d+", x) else float(x))
                                    if re.fullmatch(r"[+-]?\d+(\.\d+)?", x) else x
                                    for x in parts
                                ]
                                tp.set(vals)
                                total_set += 1
                                per_param_tally[parm_name] = per_param_tally.get(parm_name, 0) + 1
                                node_applied.append((parm_name, value_text))
                                continue
                            except Exception:
                                pass

                        v = _coerce_value((p or tp[0]), value_text)
                        if tp:
                            if not isinstance(v, (list, tuple)):
                                v = [v] * len(tp)
                            tp.set(v)
                        else:
                            p.set(v)

                        total_set += 1
                        per_param_tally[parm_name] = per_param_tally.get(parm_name, 0) + 1
                        node_applied.append((parm_name, value_text))

                    except Exception:
                        total_failed += 1

                if node_applied:
                    per_node_updates[n.path()] = node_applied

        # HUD message
        msg = f"Set total of {total_set} nodes"
        if total_skipped_missing_condition:
            msg += f" | Skipped (didn't have all parms): {total_skipped_missing_condition}"
        if total_missing:
            msg += f" | Missing parm on apply: {total_missing}"
        if total_failed:
            msg += f" | Failed: {total_failed}"
        hou.ui.displayMessage(msg, severity=hou.severityType.Message)

        # --- Build a nice HTML summary in the UI ---
        self._render_summary(per_node_updates, per_param_tally,
                             total_set, total_skipped_missing_condition, total_missing, total_failed)

    # ---------------- Summary rendering ----------------

    def _render_summary(self, per_node_updates, per_param_tally, total_set, skipped, missing, failed):
        """
        Render an HTML summary into self.summary_text.
        """
        lines = []
        lines.append("<div style='font-family: Menlo, Consolas, monospace; font-size:12px;'>")

        # Updated nodes
        upd_count = len(per_node_updates)
        lines.append(f"<h3 style='margin:4px 0;'>Updated Nodes ({upd_count})</h3>")
        if upd_count == 0:
            lines.append("<p>No nodes were updated.</p>")
        else:
            lines.append("<ul style='margin:0 0 6px 18px;'>")
            for node_path, pairs in sorted(per_node_updates.items()):
                pretty_pairs = ", ".join(f"<b>{_html_escape(p)}</b>=<span>{_html_escape(v)}</span>"
                                         for (p, v) in pairs)
                lines.append(f"<li><code>{_html_escape(node_path)}</code> — {pretty_pairs}</li>")
            lines.append("</ul>")

        # Per-parameter totals
        lines.append("<h3 style='margin:8px 0 4px;'>Parameter Totals</h3>")
        if not per_param_tally:
            lines.append("<p>No parameters provided.</p>")
        else:
            lines.append("<ul style='margin:0 0 6px 18px;'>")
            for parm_name, count in per_param_tally.items():
                lines.append(f"<li><b>{_html_escape(parm_name)}</b> &rarr; set on <b>{count}</b> node(s)</li>")
            lines.append("</ul>")

        # Footer stats
        lines.append("<hr style='border:none;border-top:1px solid #ccc;margin:6px 0;'/>")
        lines.append("<p style='margin:0;'>"
                     f"Applied: <b>{total_set}</b>"
                     f" &nbsp;|&nbsp; Skipped (missing all-parms condition): <b>{skipped}</b>"
                     f" &nbsp;|&nbsp; Missing parm: <b>{missing}</b>"
                     f" &nbsp;|&nbsp; Failed: <b>{failed}</b>"
                     "</p>")

        lines.append("</div>")
        self.summary_text.setHtml("\n".join(lines))
        # ensure the panel is visible and scrolled to top
        self.summary_group.setChecked(True)
        self.summary_text.moveCursor(QtGui.QTextCursor.Start)

    # ---------------- Ref node helpers ----------------

    def _pick_node(self):
        path = hou.ui.selectNode(title="Pick reference node")
        if path:
            self.ref_le.setText(path)
            self._refresh_ref_info()

    def _refresh_ref_info(self):
        path = self.ref_le.text().strip()
        node = hou.node(path) if path else None
        self._ref_node = node
        if node:
            info = f"{node.type().category().name()} • {node.type().name()}"
        else:
            info = ""
        self.info_lbl.setText(info)

