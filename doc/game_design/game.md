# Game

This details design decisions around the game framework and mechanics.

## Screens

### Splash screen
show logo(s), loading if needed, etc.

### Main Menu
* New game / continue
* Load game
* Options
* Credits
* Quit

### Options
Options screen can be accessed from the main menu as well as in the game.

* Music volume
* Sound volume
* Controls
* Graphics
  * Resolution
  * Fullscreen
  * Frame rate cap: 30, 60, 120, 144, 240, Unlimited
  * Vsync
  * Calibrate brightness
  * Quality
    * Performance
    * Balanced
    * Quality
    * Ultra
  * Show FPS
* Language
* Accessibility
  * Reduce motion
  * Large text
  * 
* 

### Game screen
Will draw the map, player, characters, UI

### Pause menu / inventory / map / etc.
Opened from within the game if the player pauses the game. They can manage
their inventory, upgrade their skills, change their loadout, view quests
Map is undecided at this point, since maps are separated it might need to be bespoke

## Controls

Gamepad-first, but keyboard and mouse supported too.

With playstation controls:
X: jump
Square: user assignable but defaults to physical attack
Circle, Triangle: user assignable
L1: Use potion
R1, R2, L2: user assignable

## Inventory

Limited number of slots, all items take up one slot, some items stack.

## Currency

Gold to purchase regular items, etc.
later on maybe different curriences for late game stuff


## Localization / i18n

Yes, possibly

## Character stats

* Level (governs all stats)
* Health
* Mana (Magic resource)
* Strength (Physical damage)
* Intelligence (Magical damage)

## Types of items

> Potions are special (not stored in the inventory) and quantity is capped. Potions restore x% health over a period of time.
> * Potion count and potion potency can be upgraded.
> 
> There are no mana potions, mana regenerates by itself over time. (Both health and mana are fully restored at Obelisks.)
> * Mana cap can be permanently increased.

* Equipment
* Quest items
* Consumables
  * Scrolls
  * 


## Types of equipment

* Might weapon - swords, daggers, etc.
* Magic weapon - staffs, wands, etc.
* Armor - protection against damage
* Boots - provides movement bonuses
* Amulet - provides a powerful bonus
* Ring (2) - provides bonuses
* Swords: weapons that do physical damage. Equipped in one hand.
* Wands: weapons that do magical damage. Equipped in the other hand.

## Magic elements

* Fire
* Frost
* Fairy