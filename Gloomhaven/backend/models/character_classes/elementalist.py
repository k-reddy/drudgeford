import backend.models.action_model as actions
import backend.utils.attack_shapes as shapes
from backend.models import obstacle

cards = [
    actions.ActionCard(
        attack_name="Shockwave",
        actions=[
            actions.AreaAttack(shape=shapes.line((1,0),4), strength=3),
            actions.PushAllEnemies(1, 3)
        ],
        movement=1,
        jump=False
    ),
    
    actions.ActionCard(
        attack_name="Ring of Fire",
        actions=[
            actions.AreaAttack(shape=shapes.circle(2), strength=2),
            actions.ElementAreaEffectFromSelf(
                shape=shapes.circle(2),
                element_type=obstacle.Fire
            )
        ],
        movement=1,
        jump=False
    ),
    
    actions.ActionCard(
        attack_name="Explosive Blast",
        actions=[
            actions.AreaAttack(shape=shapes.circle(2), strength=2),
            actions.WeakenEnemy(2,2),
            actions.PushAllEnemies(2, 2)
        ],
        movement=1,
        jump=False
    ),
    
    actions.ActionCard(
        attack_name="Storm of Blades",
        actions=[
            actions.AreaAttack(shape=shapes.circle(1), strength=3),
            actions.AreaAttack(shape=shapes.circle(2), strength=1),
        ],
        movement=2,
        jump=False
    ),
    
    actions.ActionCard(
        attack_name="Earthquake",
        actions=[
            actions.AreaAttack(shape=shapes.line((0,-1),3), strength=4),
            actions.MakeObstableArea(
                obstacle_type=obstacle.Wall,
                shape=shapes.bar(1,1)
            )
        ],
        movement=1,
        jump=True
    ),
    actions.ActionCard(
        attack_name="Flame Wall",
        actions=[
            actions.AreaAttack(shape=shapes.line((1,0),2), strength=3),
            actions.ElementAreaEffectFromSelf(
                shape=shapes.line((1,0), 2),
                element_type=obstacle.Fire
            )
        ],
        movement=1,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Thunder Burst",
        actions=[
            actions.AreaAttack(shape=shapes.circle(2), strength=4),
            actions.PushAllEnemies(1,2)
        ],
        movement=1,
        jump=False
    )
]

health = 4