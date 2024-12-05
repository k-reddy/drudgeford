from backend.models import action_model as actions
from backend.utils import attack_shapes as shapes

cards = [
    actions.ActionCard(
        attack_name="Crushing Slam",
        actions=[actions.SingleTargetAttack(4, 1), actions.Push(2, 1)],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Rage of Pain",
        actions=[actions.SingleTargetAttack(2, 1), actions.ChargeNextAttack(4)],
        movement=3,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Thunderous Charge",
        actions=[
            actions.AreaAttack(shape=shapes.line(3), strength=3),
            actions.Push(2, 3),
        ],
        movement=4,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Absorb Impact",
        actions=[actions.ShieldSelf(4, 2), actions.ChargeNextAttack(2)],
        movement=1,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Flesh Prison",
        actions=[actions.Pull(3, 3), actions.SingleTargetAttack(3, 1)],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Stone Flesh",
        actions=[
            actions.ShieldSelf(2, 2),
            actions.AreaAttack(shape=shapes.bar(1, 2), strength=3),
        ],
        movement=3,
        jump=False,
    ),
]

health = 6
