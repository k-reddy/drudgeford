import actions
import attack_shapes as shapes
from obstacle import Rock


cards = [
    actions.ActionCard(
        attack_name="Heavy Hammer",
        actions=[
            actions.SingleTargetAttack(
                strength=4,
                att_range=1
            ),
            actions.ChargeNextAttack(
                strength=2
            )
        ],
        movement=0,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Pickaxe Swipe",
        actions=[
            actions.AreaAttack(
                shape=shapes.arc(4),
                strength=2
            )
        ],
        movement=2,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Mason's Shield",
        actions=[
            actions.ShieldSelf(
                strength=1,
                duration=2
            ),
            actions.SingleTargetAttack(
                strength=4,
                att_range=1
            )
        ],
        movement=2,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Stone Meditation",
        actions=[
            actions.ShieldSelf(
                strength=2,
                duration=1
            ),
            actions.ModifySelfHealth(
                strength=4
            )
        ],
        movement=1,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Crystal Placebo",
        actions=[
            actions.ModifySelfHealth(strength=4),
            actions.SingleTargetAttack(
                strength=2,
                att_range=1
            ),
        ],
        movement=0,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Self Sacrifice",
        actions=[
            actions.SingleTargetAttack(
                strength=6,
                att_range=1
            ),
            actions.BlessSelf(),
            actions.ModifySelfHealth(-4)
        ],
        movement=1,
        jump=False   
    ),
    actions.ActionCard(
        attack_name="Desperate Mining",
        actions=[
            actions.AreaAttack(shape=shapes.circle(2),strength=1),
            actions.BlessSelf(),
            actions.ChargeNextAttack(strength=4),
            actions.ModifySelfHealth(-5),
        ],
        movement=0,
        jump=False
    ),
    actions.ActionCard(
        # Tax Assessment - Weaken target, pull 2, attack 3
        attack_name="Tax Assessment",
        actions=[
            actions.Pull(
                squares=2, 
                att_range=3
            ),
            actions.SingleTargetAttack(
                strength=3,
                att_range=1
            ),
            actions.WeakenEnemy(
                strength=-2,
                att_range=1
            )
        ],
        movement=3,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Stone Defense",
        actions=[
            actions.MakeObstableArea(
                obstacle_type=Rock,
                shape=shapes.bar(1,1)
            ),
            actions.ShieldAllAllies(
                strength=2,
                duration=1,
                att_range=2
            )
        ],
        movement=0,
        jump=False
    )
]
backstory = "I'm a miner"
health = 16