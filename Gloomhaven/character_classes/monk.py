import actions as actions
import attack_shapes as shapes

cards = [
    actions.ActionCard(
        attack_name="Bitter Harvest",
        actions=[
            actions.SingleTargetAttack(3,1),
            actions.ChargeNextAttack(2),
        ],
        movement=2,
        jump=True
    ),
    actions.ActionCard(
        attack_name="Sacred Cultivation",
        actions=[
            actions.ModifySelfHealth(3),
            actions.BlessSelf(),
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