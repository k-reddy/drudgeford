from backend.models import action_model as actions
from backend.utils import attack_shapes as shapes
from backend.models import obstacle

cards = [
    actions.ActionCard(
        attack_name="Flame Darts",
        actions=[
            actions.SingleTargetAttack(2, 4),
            actions.SingleTargetAttack(2, 4),
        ],
        movement=3,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Fire Trail",
        actions=[
            actions.ElementAreaEffectFromSelf(
                shape=shapes.line((1, 0), 4), element_type=obstacle.Fire
            ),
            actions.WeakenAllEnemies(1, 2),
        ],
        movement=4,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Spark Storm",
        actions=[
            actions.AreaAttack(shape=shapes.circle(1), strength=2),
        ],
        movement=3,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Burning Dash",
        actions=[
            actions.ElementAreaEffectFromSelf(
                shape=shapes.cone(2), element_type=obstacle.Fire
            ),
            actions.AreaAttack(shape=shapes.cone(2), strength=2),
        ],
        movement=5,  # Increased base movement to represent the "dash"
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Ember Shield",
        actions=[
            actions.ShieldAllAllies(1, 2, 2),
            actions.ElementAreaEffectFromSelf(
                shape=shapes.ring(2), element_type=obstacle.Fire
            ),
        ],
        movement=3,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Heat Wave",
        actions=[
            actions.WeakenAllEnemies(2, 2),
            actions.AreaAttack(shapes.circle(2), 2),
        ],
        movement=3,
        jump=True,
    ),
]

health = 4
