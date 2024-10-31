import gh_types
import attack_shapes as shapes


cards = [
# Desparate Mining - Range 2, examine stone pile. If gems found, gain shield 2, bless, heal 2. If no gems, gain weaken. Move 1 
# Stone Meditation - Skip turn, heal 4 if adjacent to stone pile, shield 2
# Tax Assessment - Weaken target, pull 2, attack 3
# Crystal Placebo - Attack 2, range 1, heal 4
# Stone Foundation - Create impassable stone barrier length 2, shield all adjacent allies
# Self Sacrifice - Attack 6, range 1, bless self but -3 health, move 1
    gh_types.ActionCard(
        attack_name="Hevvy Hammer",
        actions=[
            gh_types.SingleTargetAttack(
                strength=4,
                att_range=1
            ),
            gh_types.ChargeNextAttack(
                strength=2
            )
        ],
        movement=0,
        jump=False
    ),
    gh_types.ActionCard(
        attack_name="Pickaxe Swipe",
        actions=[
            gh_types.AreaAttack(
                shape=shapes.arc(4),
                strength=2
            )
        ],
        movement=2,
        jump=False
    ),
    gh_types.ActionCard(
        attack_name="Mason's Shield",
        actions=[
            gh_types.ShieldSelf(
                strength=1,
                duration=2
            ),
            gh_types.SingleTargetAttack(
                strength=4,
                att_range=1
            )
        ],
        movement=0,
        jump=False
    )
]
backstory = ""
health = 16