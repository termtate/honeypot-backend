from schema import AttackSchema
from ..models import Attack
from .generate import CRUDWithSession

CRUDAttack = CRUDWithSession[AttackSchema, Attack]