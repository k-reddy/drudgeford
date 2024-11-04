import action_model as action_model
import attack_shapes as shapes
from obstacle import Shadow
# from character import Skeleton


cards = [
    action_model.ActionCard(
        attack_name="Fear Mongerer",
        actions=[
            action_model.PushAllEnemies(3,2)
        ],
        movement=0,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Curse of Futility",
        actions=[
            action_model.SingleTargetAttack(3,1),
            action_model.Curse(1),
        ],
        movement=1,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Death's embrace",
        actions=[
            action_model.AreaAttack(shapes.circle(radius=2), 1)
        ],
        movement=0,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Shadow Step",
        actions=[
            action_model.SingleTargetAttack(1, 4)
        ],
        movement=4,
        jump=True
    ),
    action_model.ActionCard(
        attack_name="Soul Strike",
        actions=[
            action_model.SingleTargetAttack(4, 1),
        ],
        movement=1,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Death's Gambit",
        actions=[
            action_model.CurseAllEnemies(3),
            action_model.PushAllEnemies(1,3),
        ],
        movement=0,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Reviving Glare",
        actions=[
            action_model.SummonSkeleton()
        ],
        movement=0,
        jump=False
    ),
    action_model.ActionCard(
        # switch this to shadow that shows up around you
        attack_name="Night Owl",
        actions=[
            action_model.ElementAreaEffectFromSelf(shape=shapes.circle(2,),element_type=Shadow)
        ],
        movement=2,
        jump=False
    ),


# the theme is a character that doesn't have much health
# so has crowd control, but is rewarded for staying close to enemies
]
backstory = "I'm a necromancer. Grr."
health = 9