from backend.models import action_model as actions
from backend.utils import attack_shapes as shapes
from backend.models import obstacle

cards = [
    actions.ActionCard(
        attack_name="Cold Tears",
        actions=[
            actions.ElementAreaEffectWithTarget(
                shape=shapes.ring(1),
                element_type=obstacle.Ice,
                att_range=3
            ),
            actions.CurseAllEnemies(3)
        ],
        movement=3,
        jump=True
    ),
    actions.ActionCard(
        attack_name="Haunting Screech",
        actions=[
            actions.WeakenAllEnemies(2, 3),
            actions.PushAllEnemies(2, 3)
        ],
        movement=3,
        jump=True
    ),
    actions.ActionCard(
        attack_name="Bone Rally",
        actions=[
            actions.SingleTargetAttack(3, 2),
            actions.SummonSkeleton()
        ],
        movement=4,
        jump=True
    ),
    actions.ActionCard(
        attack_name="Psychic Torment",
        actions=[
            actions.CurseAllEnemies(3),
            actions.Pull(2, 3)
        ],
        movement=3,
        jump=True
    ),
    actions.ActionCard(
        attack_name="Blood Rain",
        actions=[
            actions.AreaAttack(
                shape=shapes.circle(2),
                strength=3
            ),
            actions.WeakenAllEnemies(1, 2)
        ],
        movement=2,
        jump=True
    ),
    actions.ActionCard(
        attack_name="Maddening Presence",
        actions=[
            actions.Curse(3),
            actions.WeakenEnemy(3, 3)
        ],
        movement=3,
        jump=True
    )
]

health = 3