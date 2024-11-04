import actions as actions
import attack_shapes as shapes
from obstacle import Shadow
# from character import Skeleton


cards = [
    actions.ActionCard(
        attack_name="Fear Mongerer",
        actions=[
            actions.PushAllEnemies(3,2)
        ],
        movement=0,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Curse of Futility",
        actions=[
            actions.SingleTargetAttack(3,1),
            actions.Curse(1),
        ],
        movement=1,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Death's embrace",
        actions=[
            actions.AreaAttack(shapes.circle(radius=2), 1)
        ],
        movement=0,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Shadow Step",
        actions=[
            actions.SingleTargetAttack(1, 4)
        ],
        movement=4,
        jump=True
    ),
    actions.ActionCard(
        attack_name="Soul Strike",
        actions=[
            actions.SingleTargetAttack(4, 1),
        ],
        movement=1,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Death's Gambit",
        actions=[
            actions.CurseAllEnemies(3),
            actions.PushAllEnemies(1,3),
        ],
        movement=0,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Reviving Glare",
        actions=[
            actions.SummonSkeleton()
        ],
        movement=0,
        jump=False
    ),
    actions.ActionCard(
        # switch this to shadow that shows up around you
        attack_name="Night Owl",
        actions=[
            actions.ElementAreaEffectFromSelf(shape=shapes.circle(2,),element_type=Shadow)
        ],
        movement=2,
        jump=False
    ),


# the theme is a character that doesn't have much health
# so has crowd control, but is rewarded for staying close to enemies
]
backstory = "I'm a necromancer. Grr."
health = 9