from backend.models import action_model as actions
from backend.utils import attack_shapes as shapes
from backend.models import obstacle

cards = [
    actions.ActionCard(
        attack_name="Cold Tears",
        actions=[
            actions.AreaAttackWithTarget(
                shape=shapes.ring(1), element_type=obstacle.Ice, att_range=3, damage=2
            ),
            actions.CurseAllEnemies(3),
        ],
        movement=3,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Piercing Screech",
        actions=[
            actions.SingleTargetAttack(2, 2, pierce=True),
            actions.PushAllEnemies(2, 3),
        ],
        movement=3,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Bone Rally",
        actions=[actions.SummonSkeleton()],
        movement=4,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Psychic Torment",
        actions=[
            actions.CurseAllEnemies(3),
            actions.AreaAttackFromSelf(shape=shapes.circle(3), strength=1),
        ],
        movement=3,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Maddening Presence",
        actions=[actions.Curse(3), actions.WeakenEnemy(3, 3)],
        movement=3,
        jump=True,
    ),
]

health = 5
