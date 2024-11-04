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
            action_model.ModifySelfHealth(3),
            action_model.BlessSelf(),
        ],
        movement=3,
        jump=False
    )
]
# Estrangement - Push 3, bless self, move 2
# Fermented Fury - Attack 2 range 1, curse target, strengthen self, move 1
# Seeds of Wrath - Bless ally, charge next attack +3, move 2
# Scythe Swipe - Attack 4 range 0, move 1, arc pattern 
# Field Runner - Heal 2, move 4, strengthen if you end next to ally
# Prayer of Spite - Attack 6 range 2, curse self, move 0
health = 12
backstory = "I'm a monk. Hiya!"