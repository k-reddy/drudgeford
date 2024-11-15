from backend.models import action_model as actions
from backend.utils import attack_shapes as shapes
from backend.models import obstacle

cards = [
    actions.ActionCard(
        attack_name="Ice Slam",
        actions=[
            actions.SingleTargetAttack(4, 1),
            actions.ElementAreaEffectFromSelf(
                shape=shapes.circle(1),
                element_type=obstacle.Ice
            )
        ],
        movement=2,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Chilling Grasp",
        actions=[
            actions.Pull(2, 3),
            actions.SingleTargetAttack(2, 1),
        ],
        movement=2,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Avalanche Charge",
        actions=[
            actions.AreaAttack(
                shape=shapes.line((1,0), 3),
                strength=3
            ),
            actions.PushAllEnemies(1, 1)
        ],
        movement=4,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Fortify",
        actions=[
            actions.ShieldSelf(3, 2),
            actions.MakeObstableArea(
                obstacle_type=obstacle.Ice,
                shape=shapes.ring(2)
            )
        ],
        movement=1,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Arctic Fury",
        actions=[
            actions.ChargeNextAttack(3),
            actions.SingleTargetAttack(3, 1)
        ],
        movement=2,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Protective Instinct",
        actions=[
            actions.ShieldAllAllies(2, 2, 2),
            actions.WeakenAllEnemies(1, 2)
        ],
        movement=2,
        jump=False
    )
]

health = 4