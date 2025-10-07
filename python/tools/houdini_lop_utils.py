"""
Houdini LOP/Solaris utility helpers.

A cohesive, idempotent helper API for recurring patterns in this repo:
- Node creation/wiring/layout/coloring
- Parm setting with safe fallbacks and expression/link helpers
- ParmTemplate creation helpers
- Solaris patterns: variant loops, configure layer, reference::2.0, assign material, set variant
- Export/introspection helpers

Design goals:
- Idempotent: helpers should be safe to call repeatedly.
- No hidden UI side effects: never change selection or focus unless explicitly requested.
- Version resilience: provide shims for parameter name drift across Houdini 20.5 → 21.x.
- Prefer expressions (chs/ch) over backtick strings where appropriate.

This module is intentionally self-contained and <= ~600 lines (PEP8-ish).
"""
from __future__ import annotations

import json
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Union

import hou

# -----------------------------
# Constants and version shims
# -----------------------------

DEFAULT_VARIANT_SET = "mtl"
DEFAULT_BIND_PURPOSE = "full"
DEFAULT_BIND_STRENGTH_MENU = "fallback"  # menu token in many builds
DEFAULT_PRIMPATH_MTL = "/ASSET/mtl"
DEFAULT_CONFIGURE_SAVE = './data/$HIPNAME/mtl_`chs("../variantname")`.usd'


def _houdini_version_tuple() -> Tuple[int, int, int]:
    v = hou.applicationVersion()
    # e.g., (21, 0, 123)
    return v[0], v[1], v[2]


# Assign Material parm name shims across versions/contexts.
ASSIGN_MATERIAL_PARM_ALIASES: Dict[str, Sequence[str]] = {
    # single vs indexed variants; string vs menu tokens may differ per build
    "nummaterials": ("nummaterials",),
    "enable1": ("enable1", "enable"),
    "primpattern1": ("primpattern1", "primpattern"),
    "ispathexpression1": ("ispathexpression1", "ispathexpression"),
    "matspecmethod1": ("matspecmethod1", "matspecmethod"),
    "matspecvexpr1": ("matspecvexpr1", "vexexpression", "matspecvexpr"),
    "parmsovermethod1": ("parmsovermethod1", "parmsovermethod"),
    "matparentpath1": ("matparentpath1", "matparentpath"),
    "matparenttype1": ("matparenttype1", "matparenttype"),
    "cvexautobind1": ("cvexautobind1", "cvexautobind"),
    "matbindingfolder1": ("matbindingfolder1", "matbindingfolder"),
    "geosubset1": ("geosubset1", "geosubset"),
    "bindpurpose1": ("bindpurpose1", "bindpurpose"),
    "bindstrength1": ("bindstrength1", "bindstrength"),
    "bindmethod1": ("bindmethod1", "bindmethod"),
    # helper parms often present on Assign Material
    "asset_path": ("asset_path",),
}

# Variant loop node type shims
VARIANT_BEGIN_TYPES = ("variantblockbegin", "begincontextoptionsblock")
VARIANT_END_TYPES = ("variantblockend", "addvariant")


# -----------------------------
# Core node helpers
# -----------------------------

def get_or_create(parent: hou.Node, node_type: str, name: str) -> hou.Node:
    """Get a child by name or create a node of type with that name under parent.
    Idempotent and safe.
    """
    node = parent.node(name)
    if node and node.type().name() == node_type:
        return node
    if node and node.type().name() != node_type:
        try:
            node.destroy()
        except Exception:
            pass
    return parent.createNode(node_type, name)


def connect(dst: hou.Node, input_index: int, src: Optional[hou.Node]) -> None:
    """Connect src → dst at given index if src is not None, else clear input."""
    if src is None:
        try:
            dst.setInput(input_index, None)
        except Exception:
            pass
        return
    if dst.inputConnections() and input_index < len(dst.inputs()):
        # Avoid duplicate rewire if already connected
        if dst.inputs()[input_index] is src:
            return
    dst.setInput(input_index, src)


def connect_next(merge_like: hou.Node, src: hou.Node) -> None:
    """Append next available input on a multi-input node (merge-like)."""
    merge_like.setNextInput(src)


def ensure_subnet_inputs(subnet: hou.Node, min_inputs: int = 1, max_inputs: int = 4) -> None:
    """Hint UI about subnet connector counts using userData."""
    try:
        subnet.setUserData("mininputs", str(min_inputs))
        subnet.setUserData("maxinputs", str(max_inputs))
    except Exception:
        pass


def layout(nodes: Iterable[hou.Node]) -> None:
    try:
        parent = None
        nodes_list = list(nodes)
        if nodes_list:
            parent = nodes_list[0].parent()
        if parent:
            parent.layoutChildren(nodes_list)
    except Exception:
        pass


def color(node: hou.Node, rgb: Tuple[float, float, float]) -> None:
    try:
        node.setColor(hou.Color(*rgb))
    except Exception:
        pass


# -----------------------------
# Parm helpers
# -----------------------------

def _set_parm_safe(parm: Optional[hou.Parm], value: Union[str, int, float]) -> None:
    if parm is None:
        return
    try:
        parm.set(value)
    except Exception:
        pass


def expr(parm: Optional[hou.Parm], expression: str, lang: hou.exprLanguage = hou.exprLanguage.Hscript) -> None:
    if parm is None:
        return
    try:
        parm.setExpression(expression, language=lang)
    except Exception:
        pass


def link_chs(dst_parm: Optional[hou.Parm], src_rel_path: str) -> None:
    """Set dst parm to an HScript string-expr link to chs(src)."""
    if dst_parm is None:
        return
    expr(dst_parm, f'chs("{src_rel_path}")', hou.exprLanguage.Hscript)


def link_ch(dst_parm: Optional[hou.Parm], src_rel_path: str) -> None:
    if dst_parm is None:
        return
    expr(dst_parm, f'ch("{src_rel_path}")', hou.exprLanguage.Hscript)


def set_parms(node: hou.Node, parms: Dict[str, Union[str, int, float]], aliases: Optional[Dict[str, Sequence[str]]] = None) -> None:
    """Safely set parms on a node with fallback aliases per key.

    parms: canonical_name → value
    aliases: canonical_name → tuple(candidate_names)
    """
    aliases = aliases or {}
    for key, val in parms.items():
        names = (key,)
        if key in aliases:
            names = tuple(aliases[key])
        found = False
        for nm in names:
            p = node.parm(nm)
            if p is not None:
                _set_parm_safe(p, val)
                found = True
                break
        if not found:
            # best-effort: ignore silently
            pass


# -----------------------------
# ParmTemplate helpers
# -----------------------------

def _append_or_replace(ptg: hou.ParmTemplateGroup, parm_t: hou.ParmTemplate) -> None:
    if ptg.find(parm_t.name()) is not None:
        ptg.replace(parm_t.name(), parm_t)
    else:
        ptg.append(parm_t)


def add_string(ptg: hou.ParmTemplateGroup, name: str, label: str, default: str = "", string_type: hou.stringParmType = hou.stringParmType.Regular, tags: Optional[Dict[str, str]] = None) -> None:
    p = hou.StringParmTemplate(name, label, 1, default_value=(default,), string_type=string_type)
    if tags:
        p.setTags(tags)
    _append_or_replace(ptg, p)


def add_menu(ptg: hou.ParmTemplateGroup, name: str, label: str, items: Sequence[str], labels: Optional[Sequence[str]] = None, default_index: int = 0) -> None:
    labels = labels or items
    p = hou.MenuParmTemplate(name, label, menu_items=tuple(items), menu_labels=tuple(labels), default_value=default_index)
    _append_or_replace(ptg, p)


def add_toggle(ptg: hou.ParmTemplateGroup, name: str, label: str, default: bool = False) -> None:
    p = hou.ToggleParmTemplate(name, label, default_value=default)
    _append_or_replace(ptg, p)


def add_separator(ptg: hou.ParmTemplateGroup, name: str) -> None:
    _append_or_replace(ptg, hou.SeparatorParmTemplate(name))


# -----------------------------
# Solaris patterns
# -----------------------------

def build_variant_loop(parent: hou.Node, begin_name: str = "variantblock_begin1", end_name: str = "variantblock_end1") -> Tuple[hou.Node, hou.Node]:
    """Create or get a variant block begin/end pair with version shims.

    Returns: (begin_node, end_node)
    """
    begin = None
    end = None
    # try preferred names/types first
    for t in VARIANT_BEGIN_TYPES:
        if begin is None:
            begin = get_or_create(parent, t, begin_name) if parent.node(begin_name) is None or parent.node(begin_name).type().name() != t else parent.node(begin_name)
            if begin is not None and begin.type().name() == t:
                break
    if begin is None:
        begin = parent.createNode(VARIANT_BEGIN_TYPES[0], begin_name)

    for t in VARIANT_END_TYPES:
        if end is None:
            end = get_or_create(parent, t, end_name) if parent.node(end_name) is None or parent.node(end_name).type().name() != t else parent.node(end_name)
            if end is not None and end.type().name() == t:
                break
    if end is None:
        end = parent.createNode(VARIANT_END_TYPES[0], end_name)

    return begin, end


def build_configure_layer(parent: hou.Node, name: str = "configure_layer1", savepath: Optional[str] = None) -> hou.Node:
    node = get_or_create(parent, "configurelayer", name)
    if savepath is None:
        savepath = DEFAULT_CONFIGURE_SAVE
    _set_parm_safe(node.parm("setsavepath"), 1)
    _set_parm_safe(node.parm("setinputlayerexplicit"), 1)
    _set_parm_safe(node.parm("setstagemetadata"), 1)
    _set_parm_safe(node.parm("savepath"), savepath)
    return node


def build_reference2(parent: hou.Node, name: str = "reference2", primpath: str = DEFAULT_PRIMPATH_MTL, refprimpath: Optional[str] = None) -> hou.Node:
    node = get_or_create(parent, "reference::2.0", name)
    if refprimpath is None:
        refprimpath = primpath
    set_parms(node, {
        "primpath": primpath,
        "refprimpath": refprimpath,
        "enable": 1,
        "input_group": 1,
        "createprims": "on",
        "reftype": "file",
        "instanceable": 0,
        "files_group": 1,
        "num_files": 0,
        "primkind": "__automatic__",
        "parentprimtype": "UsdGeomXform",
        "handlemissingfiles": "error",
        "preop": "none",
        "refeditop": "prependfront",
    })
    return node


def configure_assign_material(node: hou.Node, primpattern_expr: str, vexpression_expr: str, bind_purpose_expr: str, bind_strength_expr: str) -> None:
    """Configure an Assign Material node in a version-resilient way.

    primpattern_expr/vexpression_expr/bind_*_expr are expressions (chs/ch) strings.
    """
    parms = {
        "nummaterials": 1,
        "enable1": 1,
        "primpattern1": primpattern_expr,
        "ispathexpression1": 0,
        "matspecmethod1": "vexpr",  # in some builds it expects token; in others 2
        "matspecvexpr1": vexpression_expr,
        "parmsovermethod1": "none",
        "matparentpath1": "/materials",
        "matparenttype1": "UsdGeomScope",
        "cvexautobind1": 1,
        "matbindingfolder1": 1,
        "geosubset1": 0,
        "bindpurpose1": bind_purpose_expr,
        "bindstrength1": bind_strength_expr,
        "bindmethod1": "direct",
    }
    set_parms(node, parms, ASSIGN_MATERIAL_PARM_ALIASES)

    # If matspecmethod expects an int in this build, fallback to 2
    p = None
    for nm in ASSIGN_MATERIAL_PARM_ALIASES.get("matspecmethod1", ("matspecmethod1",)):
        p = node.parm(nm)
        if p:
            break
    try:
        if p and isinstance(p.eval(), (int, float)):
            _set_parm_safe(p, 2)
    except Exception:
        pass


def setup_setvariant_from_end(setvariant: hou.Node, v_end: hou.Node) -> None:
    """Wire Set Variant to pick its variantset/name from the variant end node."""
    _set_parm_safe(setvariant.parm("num_variants"), 1)
    _set_parm_safe(setvariant.parm("enable1"), 1)
    expr(setvariant.parm("primpattern1"), 'lopinputprims(".", 0)')
    expr(setvariant.parm("variantset1"), f'chs("../{v_end.name()}/variantset")')
    expr(setvariant.parm("variantname1"), f'chs("../{v_end.name()}/variantname")')


def build_solaris_material_variant_subnet(parent: hou.Node, name: str = "component_material_custom") -> hou.Node:
    """High-level builder to create the common material variant subnet pattern.

    Creates a subnet with spare parms and the internal graph:
    - Variant loop (Begin/End) merging Configure Layer and Begin branch
    - Reference::2.0 over /ASSET/mtl
    - Assign Material configured from spare parms
    - Set Variant driven by End node
    - Output
    Idempotent, does not change selection.
    """
    subnet = get_or_create(parent, "subnet", name)
    ensure_subnet_inputs(subnet, 2, 4)

    # Spare parms
    ptg = hou.ParmTemplateGroup()
    add_string(ptg, "variantset", "Variant Set", DEFAULT_VARIANT_SET)
    add_string(ptg, "variantname", "Variant Name Default", "$OS")
    add_separator(ptg, "sep1")
    add_string(ptg, "primpattern1", "Primitives", "%type:Mesh", tags={
        "script_action": "import loputils\nloputils.selectPrimsInParm(kwargs, True, allowinstanceproxies=True)",
        "script_action_help": "Select primitives in the Scene Viewer or Scene Graph Tree pane.",
        "script_action_icon": "BUTTONS_reselect",
        "sidefx::usdpathtype": "primlist",
    })
    add_string(ptg, "matspecvexpr1", "Vexpression", 'chs("asset_path")+"/"+@primname;', tags={
        "editor": "1", "editorlang": "vex", "editorlines": "5-20",
    })
    add_string(ptg, "bindpurpose1", "Purpose", DEFAULT_BIND_PURPOSE)
    add_menu(ptg, "bindstrength1", "Strength", ("fallback", "strong", "weak"), ("Default", "Stronger than Descendants", "Weaker than Descendants"), 0)
    subnet.setParmTemplateGroup(ptg)

    # Internal nodes
    assign = get_or_create(subnet, "assignmaterial", "assign_material1")
    ref2 = get_or_create(subnet, "reference::2.0", "reference2")
    v_begin, v_end = build_variant_loop(subnet)
    cfg = build_configure_layer(subnet, "mtl_config1", DEFAULT_CONFIGURE_SAVE)
    setvar = get_or_create(subnet, "setvariant", "setvariant1")
    out = get_or_create(subnet, "output", "OUT")

    # Reference defaults
    build_reference2(subnet, "reference2", DEFAULT_PRIMPATH_MTL, DEFAULT_PRIMPATH_MTL)

    # Assign parms from spare parms
    configure_assign_material(
        assign,
        primpattern_expr='chs("../primpattern1")',
        vexpression_expr='chs("../matspecvexpr1")',
        bind_purpose_expr='chs("../bindpurpose1")',
        bind_strength_expr='ch("../bindstrength1")',
    )

    # Variant loop wiring: ref2 inputs 0<-v_begin, 1<-cfg; merge via end using setInput slots
    connect(ref2, 0, v_begin)
    connect(ref2, 1, cfg)

    # Depending on end node type, inputs differ; try typical patterns
    try:
        # addvariant: input 1 payload, input 2 passthrough begin
        connect(v_end, 1, assign)  # connect later after we have assign input
        connect(v_end, 2, v_begin)
    except Exception:
        pass

    # setvariant after v_end
    connect(setvar, 0, v_end)
    setup_setvariant_from_end(setvar, v_end)

    # Wire assign after reference chain initially, then into end
    connect(assign, 0, ref2)

    # Output at the end
    connect(out, 0, setvar)

    # External inputs mapping inside subnet (indirect inputs)
    try:
        sub_inputs = subnet.indirectInputs()
        if len(sub_inputs) > 0:
            connect(v_begin, 0, sub_inputs[0])
            connect(v_end, 0, sub_inputs[0])  # mirror original pattern
        if len(sub_inputs) > 1:
            connect(cfg, 0, sub_inputs[1])
    except Exception:
        pass

    layout(subnet.children())

    # Defaults on spare parms
    _set_parm_safe(subnet.parm("variantset"), DEFAULT_VARIANT_SET)
    _set_parm_safe(subnet.parm("variantname"), "$OS")
    _set_parm_safe(subnet.parm("primpattern1"), "%type:Mesh")
    _set_parm_safe(subnet.parm("matspecvexpr1"), 'chs("asset_path")+"/"+@primname;')
    _set_parm_safe(subnet.parm("bindpurpose1"), DEFAULT_BIND_PURPOSE)
    _set_parm_safe(subnet.parm("bindstrength1"), DEFAULT_BIND_STRENGTH_MENU)

    return subnet


# -----------------------------
# Export / Introspection
# -----------------------------

def export_as_code(node: hou.Node) -> str:
    """Return a minimal Python snippet that recreates a node under its parent."""
    parent_path = node.parent().path()
    t = node.type().name()
    name = node.name()
    lines = [
        "import hou",
        f'parent = hou.node("{parent_path}")',
        f'n = parent.createNode("{t}", "{name}")',
    ]
    # Basic parms dump (skip empty or default looking values best-effort)
    try:
        for p in node.parms():
            if p.isAtDefault():
                continue
            if p.hasExpression():
                expr_lang = p.expressionLanguage()
                lang = "hou.exprLanguage.Python" if expr_lang == hou.exprLanguage.Python else "hou.exprLanguage.Hscript"
                lines.append(f'n.parm("{p.name()}").setExpression({p.expression().__repr__()}, language={lang})')
            else:
                val = p.eval()
                if isinstance(val, str):
                    lines.append(f'n.parm("{p.name()}").set({val.__repr__()})')
                else:
                    lines.append(f'n.parm("{p.name()}").set({val})')
    except Exception:
        pass
    return "\n".join(lines)


def dump_parm_templates_to_json(node: hou.Node, indent: int = 2) -> str:
    """Return JSON of the node's spare parameter templates (not built-in parms)."""
    ptg = node.parmTemplateGroup()
    data = []
    for pt in ptg.entries():
        data.append({
            "name": pt.name(),
            "label": pt.label(),
            "type": type(pt).__name__,
        })
    return json.dumps(data, indent=indent)


def show_clickable_path(node: hou.Node) -> str:
    """Return a display string for the node path (callers may copy to clipboard)."""
    return node.path()


# -----------------------------
# Minimal quick cookbook in docstring for easy access
# -----------------------------
__doc__ += """

Quick Cookbook:
- Create or get a node and connect:
    parent = hou.node('/stage')
    ref = get_or_create(parent, 'reference::2.0', 'reference2')
    cfg = build_configure_layer(parent, 'configure_layer1')
    connect(ref, 1, cfg)

- Configure Assign Material safely:
    assign = get_or_create(parent, 'assignmaterial', 'assign1')
    configure_assign_material(assign,
        primpattern_expr='chs("../primpattern1")',
        vexpression_expr='chs("../matspecvexpr1")',
        bind_purpose_expr='chs("../bindpurpose1")',
        bind_strength_expr='ch("../bindstrength1")')

- Build a reusable material variant subnet under /stage:
    stage = hou.node('/stage')
    sub = build_solaris_material_variant_subnet(stage, 'component_material_custom')

- ParmTemplate helpers:
    ptg = hou.ParmTemplateGroup()
    add_string(ptg, 'variantset', 'Variant Set', 'mtl')
    add_menu(ptg, 'bindstrength1', 'Strength', ('fallback','strong','weak'))

- Export helpers:
    code = export_as_code(sub)
    spec = dump_parm_templates_to_json(sub)
"""
