import action_model as action_model
import attack_shapes as shapes

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
            action_model.HealAlly(strength=4, att_range=2),
            action_model.BlessAndChargeAlly(att_range=2, strength=2),
        ],
        movement=3,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Estrangement",
        actions=[
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
        movement=1,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Seeds of Wrath",
        actions=[
            action_model.BlessAndChargeAlly(2,3),
        ],
        movement=2,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Scythe Swipe",
        actions=[
            action_model.SingleTargetAttack(4,1)
        ],
        movement=2,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Field Runner",
        actions=[
            action_model.ModifySelfHealth(2),
            action_model.SingleTargetAttack(2,1)
        ],
        movement=4,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Prayer of Spite",
        actions=[
            action_model.SingleTargetAttack(6,2),
            action_model.CurseSelf()
        ],
        movement=0,
        jump=False
    )
]
health = 12
backstory = "I'm a monk. Hiya!"