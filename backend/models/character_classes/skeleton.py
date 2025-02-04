from backend.models import action_model as actions
from backend.utils import attack_shapes as shapes
from backend.models import obstacle

cards = [
    actions.ActionCard(
        attack_name="Shield Wall",
        actions=[actions.ShieldAllAllies(2, 2, 2)],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Combat Stance",
        actions=[actions.SingleTargetAttack(3, 1), actions.ShieldSelf(2, 2)],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Shield Bash",
        actions=[actions.SingleTargetAttack(3, 1), actions.Push(2, 1)],
        movement=3,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Sword Dance",
        actions=[
            actions.AreaAttackFromSelf(shape=shapes.arc(3), strength=2),
            actions.Fortify(2),
        ],
        movement=3,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Undying Warrior",
        actions=[actions.ModifySelfHealth(-1), actions.ShieldSelf(4, 2)],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Grave Line",
        actions=[actions.AreaAttackFromSelf(shape=shapes.line(3), strength=2)],
        movement=2,
        jump=False,
    ),
]

health = 4
