import backend.models.action_model as action_model
from backend.utils import attack_shapes as shapes

cards = [
    action_model.ActionCard(
        attack_name="Bitter Harvest",
        actions=[
            action_model.SingleTargetAttack(3,1),
            action_model.ChargeNextAttack(2),
        ],
        movement=2,
        jump=True
    ),
    action_model.ActionCard(
        attack_name="Sacred Cultivation",
        actions=[
            action_model.BlessAndChargeAlly(att_range=2, strength=2),
            action_model.SingleTargetAttack(3,1)
        ],
        movement=3,
        jump=True
    ),
    action_model.ActionCard(
        attack_name="Estrangement",
        actions=[
            action_model.HealAlly(4, 2),
            action_model.Push(3,2),
            action_model.BlessSelf(),
        ],
        movement=2,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Fermented Fury",
        actions=[
            action_model.SingleTargetAttack(2,1),
            action_model.Curse(1),
            action_model.ChargeNextAttack(2),
        ],
        movement=2,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Seeds of Wrath",
        actions=[
            action_model.BlessAndChargeAlly(2,3),
            action_model.CurseSelf(),
            action_model.AreaAttack(shapes.line((0,1), 5),4)
        ],
        movement=2,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Scythe Swipe",
        actions=[
            action_model.SingleTargetAttack(5,1)
        ],
        movement=3,
        jump=True
    ),
    action_model.ActionCard(
        attack_name="Healing Blast",
        actions=[
            action_model.ModifySelfHealth(4),
            action_model.HealAlly(4,3)
        ],
        movement=3,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Prayer of Spite",
        actions=[
            action_model.SingleTargetAttack(6,2),
            action_model.HealAlly(3,2),
            action_model.CurseSelf()
        ],
        movement=2,
        jump=False
    )
]
health = 12
backstory = "I'm a monk. Hiya!"