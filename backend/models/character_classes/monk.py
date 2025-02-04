import backend.models.action_model as action_model
from backend.utils import attack_shapes as shapes

cards = [
    action_model.ActionCard(
        attack_name="Bitter Harvest",
        actions=[
            action_model.SingleTargetAttack(3, 3, pierce=True),
            action_model.Fortify(2),
        ],
        movement=2,
        jump=True,
    ),
    action_model.ActionCard(
        attack_name="Sacred Cultivation",
        actions=[
            action_model.SingleTargetAttack(3, 1),
            action_model.BlessAndFortifyAlly(att_range=2, strength=2),
        ],
        movement=3,
        jump=True,
    ),
    action_model.ActionCard(
        attack_name="Estrangement",
        actions=[
            action_model.HealAlly(4, 2),
            action_model.Push(3, 2),
            action_model.BlessSelf(),
        ],
        movement=2,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Fermented Fury",
        actions=[
            action_model.SingleTargetAttack(2, 1, pierce=True),
            action_model.Curse(1),
            action_model.Fortify(2),
        ],
        movement=2,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Seeds of Wrath",
        actions=[
            action_model.AreaAttackWithTarget(
                shape=shapes.line(3), damage=3, att_range=2
            ),
            action_model.BlessAndFortifyAlly(2, 3),
            action_model.CurseSelf(),
        ],
        movement=2,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Scythe Swipe",
        actions=[
            action_model.Pull(2, 3),
            action_model.AreaAttackFromSelf(shapes.arc(3), 4),
        ],
        movement=2,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Healing Blast",
        actions=[action_model.ModifySelfHealth(4), action_model.HealAlly(4, 3)],
        movement=3,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Prayer of Spite",
        actions=[
            action_model.SingleTargetAttack(6, 2),
            action_model.HealAlly(3, 2),
            action_model.CurseSelf(),
        ],
        movement=2,
        jump=False,
    ),
]
health = 10
backstory = """Abandoned to a monastery after their family faced three failed harvests, this warrior-farmer channels their bitterness over their abandonment into martial prowess. Years of tending the monastery's fields have taught them that growth and destruction go hand in hand. They wield traditional farming implements as weapons, blessing allies while cursing enemies. A versatile and supportive fighter who combines mobility and melee attacks with the ability to heal and empower allies."""
