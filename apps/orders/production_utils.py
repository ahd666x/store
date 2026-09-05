import ast
import json
import logging
import operator
import re

from apps.catalog.models import Material
from apps.production.models import PaintingProcess

logger = logging.getLogger(__name__)


def cm_to_mm(cm):
    return cm * 10


def mm_to_cm(mm):
    return mm / 10


def parse_size_string(size_str):
    size_str = str(size_str or '').strip()
    if not size_str or size_str.lower() in {'nan', 'استاندارد'}:
        return {}
    normalized = re.sub(r'[×xX*]', 'x', size_str)
    numbers = re.findall(r'\d+', normalized)
    result = {}
    if len(numbers) >= 1:
        result['length'] = int(numbers[0])
    if len(numbers) >= 2:
        result['width'] = int(numbers[1])
    if len(numbers) >= 3:
        result['height'] = int(numbers[2])
    return result


def compute_size_diff(product, order_item):
    length_diff_mm = 0
    width_diff_mm = 0
    height_diff_mm = 0

    if product.length is not None and order_item.length is not None:
        length_diff_cm = order_item.length - product.length
        length_diff_mm = cm_to_mm(length_diff_cm)

    if product.width is not None and order_item.width is not None:
        width_diff_cm = order_item.width - product.width
        width_diff_mm = cm_to_mm(width_diff_cm)

    if product.height is not None and order_item.height is not None:
        height_diff_cm = order_item.height - product.height
        height_diff_mm = cm_to_mm(height_diff_cm)

    if length_diff_mm == 0 and width_diff_mm == 0 and height_diff_mm == 0:
        return {}

    return {
        'length_diff': length_diff_mm,
        'width_diff': width_diff_mm,
        'height_diff': height_diff_mm,
    }


_ALLOWED_NAMES = {'length', 'width', 'height'}
_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}


def _eval_node(node, variables):
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, variables)
    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPS:
            raise ValueError(f"Operator {op_type.__name__} not allowed")
        left = _eval_node(node.left, variables)
        right = _eval_node(node.right, variables)
        return _ALLOWED_OPS[op_type](left, right)
    elif isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPS:
            raise ValueError(f"Unary operator {op_type.__name__} not allowed")
        operand = _eval_node(node.operand, variables)
        return _ALLOWED_OPS[op_type](operand)
    elif isinstance(node, ast.Name):
        if node.id not in _ALLOWED_NAMES:
            raise ValueError(f"Variable {node.id} not allowed")
        return variables[node.id]
    elif isinstance(node, ast.Constant):
        return node.value
    else:
        raise ValueError(f"Node type {type(node).__name__} not allowed")


def apply_size_adjustment(original_length, original_width, diff_dict, rule):
    if not rule or not diff_dict:
        return (float(original_length), float(original_width))

    expr = (
        rule
        .replace('length_diff', str(diff_dict.get('length_diff', 0)))
        .replace('width_diff', str(diff_dict.get('width_diff', 0)))
        .replace('height_diff', str(diff_dict.get('height_diff', 0)))
    )

    try:
        tree = ast.parse(expr, mode='eval')
        variables = {'length': float(original_length), 'width': float(original_width)}
        new_length = _eval_node(tree, variables)
        return (new_length, float(original_width))
    except Exception:
        logger.exception("Error evaluating size adjustment rule: %s", rule)
        return (float(original_length), float(original_width))


def apply_width_adjustment(original_length, original_width, diff_dict, rule):
    if not rule or not diff_dict:
        return (float(original_length), float(original_width))

    expr = (
        rule
        .replace('length_diff', str(diff_dict.get('length_diff', 0)))
        .replace('width_diff', str(diff_dict.get('width_diff', 0)))
        .replace('height_diff', str(diff_dict.get('height_diff', 0)))
    )

    try:
        tree = ast.parse(expr, mode='eval')
        variables = {'length': float(original_length), 'width': float(original_width)}
        new_width = _eval_node(tree, variables)
        return (float(original_length), new_width)
    except Exception:
        logger.exception("Error evaluating width adjustment rule: %s", rule)
        return (float(original_length), float(original_width))


def apply_height_adjustment(original_length, original_width, diff_dict, rule):
    if not rule or not diff_dict:
        return (float(original_length), float(original_width))

    expr = (
        rule
        .replace('length_diff', str(diff_dict.get('length_diff', 0)))
        .replace('width_diff', str(diff_dict.get('width_diff', 0)))
        .replace('height_diff', str(diff_dict.get('height_diff', 0)))
    )

    try:
        tree = ast.parse(expr, mode='eval')
        variables = {'length': float(original_length), 'width': float(original_width)}
        result = _eval_node(tree, variables)
        if isinstance(result, (int, float)):
            if 'width' in rule.replace('width_diff', ''):
                return (float(original_length), float(result))
            return (float(result), float(original_width))
        return (float(original_length), float(original_width))
    except Exception:
        logger.exception("Error evaluating height adjustment rule: %s", rule)
        return (float(original_length), float(original_width))


def update_barcode_size(original_barcode, new_length, new_width, order_item_id=None, new_height=None):
    if not original_barcode:
        return original_barcode

    if new_height is not None and float(new_height) > 0:
        new_size = f"{int(new_length)}x{int(new_width)}x{int(new_height)}"
    else:
        new_size = f"{int(new_length)}x{int(new_width)}"
    result = re.sub(r'\d+(?:x\d+){1,2}', new_size, original_barcode)
    if result == original_barcode:
        result = f"{original_barcode}.{new_size}"

    if order_item_id is not None:
        result = f"{result}.item{order_item_id}"

    return result


def get_material_for_color(color_code, mapping=None):
    if mapping and color_code in mapping:
        material_name = mapping[color_code]
        material = Material.objects.filter(name=material_name).first()
        if not material:
            logger.warning("متریال '%s' برای رنگ '%s' در دیتابیس یافت نشد", material_name, color_code)
        return material
    return None


def get_painting_process_for_color(color_code):
    if not color_code:
        return None

    for process in PaintingProcess.objects.filter(is_active=True):
        if str(color_code).strip() in process.color_codes:
            return process
    return None


def get_item_color_assignments(order_item):
    assignments = []
    seen = set()

    order_colors = order_item.ordercolor.all()
    if order_colors.exists():
        for c in order_colors:
            if c.code and c.code != 'nan':
                key = (c.part, str(c.code))
                if key not in seen:
                    seen.add(key)
                    assignments.append(key)
    else:
        default = order_item.product.default_colors or {}
        for part, code in default.items():
            if code and code != 'nan':
                key = (part, str(code))
                if key not in seen:
                    seen.add(key)
                    assignments.append(key)

    return assignments


def _parse_default_colors(product):
    default = product.default_colors or {}
    if isinstance(default, str):
        try:
            default = json.loads(default) or {}
        except (json.JSONDecodeError, TypeError):
            default = {}
    return default
