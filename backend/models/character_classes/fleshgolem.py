from backend.models import action_model as actions
from backend.utils import attack_shapes as shapes

cards = [
    actions.ActionCard(
        attack_name="Crushing Slam",
        actions=[actions.SingleTargetAttack(2, 1, knock_down=True), actions.Push(2, 1)],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Rage of Pain",
        actions=[actions.SingleTargetAttack(2, 1), actions.Fortify(3)],
        movement=3,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Thunderous Charge",
        actions=[
            actions.AreaAttackFromSelf(shape=shapes.line(3), strength=2),
            actions.Push(2, 3),
        ],
        movement=4,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Absorb Impact",
        actions=[actions.ShieldSelf(3, 2), actions.Fortify(1)],
        movement=1,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Flesh Prison",
        actions=[actions.Pull(3, 3), actions.SingleTargetAttack(2, 1)],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Stone Flesh",
        actions=[
            actions.ShieldSelf(2, 2),
            actions.AreaAttackFromSelf(shape=shapes.bar(1, 2), strength=1),
        ],
        movement=3,
        jump=False,
    ),
]

health = 6
