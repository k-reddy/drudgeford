from backend.models import action_model as actions
from backend.utils import attack_shapes as shapes
from backend.models import obstacle

cards = [
    actions.ActionCard(
        attack_name="Dark Ritual",
        actions=[
            actions.CurseAllEnemies(2),
            actions.BlessAllAllies(2)
        ],
        movement=2,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Void Circle",
        actions=[
            actions.ElementAreaEffectFromSelf(
                shape=shapes.circle(2),
                element_type=obstacle.Shadow
            ),
            actions.WeakenAllEnemies(2, 2)
        ],
        movement=1,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Soul Link",
        actions=[
            actions.BlessAndChargeAlly(2, 3),
            actions.BlessAndChargeAlly(2, 3)
        ],
        movement=1,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Shadow Aegis",
        actions=[
            actions.ShieldAllAllies(3, 2, 3),
            actions.ElementAreaEffectFromSelf(
                shape=shapes.ring(2),
                element_type=obstacle.Shadow
            )
        ],
        movement=1,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Curse of Weakness",
        actions=[
            actions.WeakenEnemy(3, 3),
            actions.CurseAllEnemies(2)
        ],
        movement=2,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Dark Blessing",
        actions=[
            actions.ChargeNextAttack(3),
            actions.ElementAreaEffectFromSelf(
                shape=shapes.circle(1),
                element_type=obstacle.Shadow
            )
        ],
        movement=1,
        jump=False
    )
]

health = 4