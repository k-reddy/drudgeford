import backend.models.action_model as action_model
from ...utils import attack_shapes as shapes
from backend.models.obstacle import Shadow

cards = [
    action_model.ActionCard(
        attack_name="Fear Mongerer",
        actions=[
            action_model.AreaAttackFromSelf(shapes.circle(2), 2),
            action_model.PushAllEnemies(3, 2),
        ],
        movement=0,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Curse of Futility",
        actions=[
            action_model.SingleTargetAttack(2, 3, pierce=True),
            action_model.Curse(3),
        ],
        movement=2,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Life Drain",
        actions=[
            action_model.AreaAttackWithTarget(
                shape=shapes.circle(radius=1), damage=4, att_range=2
            ),
            action_model.ModifySelfHealth(4),
        ],
        movement=2,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Shadow Step",
        actions=[
            action_model.AreaAttackFromSelf(shapes.circle(1), 2, Shadow),
            action_model.ModifySelfHealth(3),
        ],
        movement=4,
        jump=True,
    ),
    action_model.ActionCard(
        attack_name="Soul Strike",
        actions=[
            action_model.SingleTargetAttack(4, 1, pierce=True),
            action_model.Curse(1),
        ],
        movement=1,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Death's Embrace",
        actions=[
            action_model.CurseAllEnemies(3),
            action_model.AreaAttackWithTarget(
                shape=shapes.ring(1), damage=4, element_type=Shadow, att_range=2
            ),
            action_model.PushAllEnemies(1, 3),
        ],
        movement=0,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Reviving Glare",
        actions=[action_model.SummonSkeleton()],
        movement=2,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Shadow Tendril",
        actions=[
            action_model.AreaAttackFromSelf(shapes.arc(4), 3, element_type=Shadow),
        ],
        movement=3,
        jump=False,
    ),
    # the theme is a character that doesn't have much health
    # so has crowd control, but is rewarded for staying close to enemies
]

health = 9

backstory = """After losing their sibling to disease, this former town resident devoted themselves to the dark arts, spending years mastering forbidden rituals to bridge the gap between life and death so they can talk together again. While they hated their sibling in life, in death their spirit is the only one who knows the location of the family treasure, a cheap but sentimental tortilla press. Now banished from their hometown for using the dark arts, they command shadows and raise the dead in their obsessive quest to recover this simple but priceless piece of their past. A fragile but powerful controller who must use their ability to curse and summon shadows to protect themselves as they deal out wide melee area attacks."""
