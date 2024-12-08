from backend.models import action_model as actions
from backend.utils import attack_shapes as shapes
from backend.models import obstacle

healer_support_cards = [
    actions.ActionCard(
        attack_name="Healing Wave",
        actions=[actions.HealAllAllies(3, 3), actions.BlessAllAllies(2)],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Protective Barrier",
        actions=[
            actions.ShieldAllAllies(3, 2, 3),
            actions.AreaAttackFromSelf(
                shape=shapes.circle(1), element_type=obstacle.Fire, strength=2
            ),
        ],
        movement=1,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Rejuvenating Touch",
        actions=[actions.HealAlly(5, 1), actions.BlessAndFortifyAlly(2, 1)],
        movement=3,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Mass Restoration",
        actions=[
            actions.HealAllAllies(2, 2),
            actions.ShieldAllAllies(2, 2, 2),
            actions.ModifySelfHealth(-2),
        ],
        movement=1,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Holy Nova",
        actions=[actions.SingleTargetAttack(2, 3), actions.HealAllAllies(2, 3)],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Divine Protection",
        actions=[
            actions.ShieldSelf(2, 2),
            actions.ShieldAllAllies(2, 1, 2),
            actions.Teleport(3),
        ],
        movement=0,
        jump=False,
    ),
]

health = 4
