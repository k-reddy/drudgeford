from backend.models import action_model as actions
from backend.utils import attack_shapes as shapes
from backend.models import obstacle

cards = [
    actions.ActionCard(
        attack_name="Protective Snares",
        actions=[
            actions.ShieldAllAllies(2, 2, 3),
            actions.MakeObstableArea(
                obstacle_type=obstacle.Trap,
                shape=shapes.bar(1,1)
            )
        ],
        movement=3,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Warming Fire",
        actions=[
            actions.ElementAreaEffectFromSelf(
                shape=shapes.circle(1),
                element_type=obstacle.Fire
            ),
            actions.HealAllAllies(2, 2)
        ],
        movement=2,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Trap Network",
        actions=[
            actions.MakeObstableArea(
                obstacle_type=obstacle.Trap,
                shape=shapes.ring(2)
            ),
            actions.Pull(2, 3)
        ],
        movement=2,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Good Hunting",
        actions=[
            actions.SingleTargetAttack(4,1),
            actions.BlessAndChargeAlly(3, 2)
        ],
        movement=2,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Slow Death",
        actions=[
            actions.SingleTargetAttack(4,2),
            actions.CurseAllEnemies(2)
        ],
        movement=3,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Shadow Attack",
        actions=[
            actions.ElementAreaEffectFromSelf(shapes.circle(2),obstacle.Shadow),
            actions.Pull(2, 3),
            actions.SingleTargetAttack(3, 1)
        ],
        movement=2,
        jump=False
    )
]

health = 6