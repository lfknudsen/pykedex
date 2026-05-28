# Pykédex

A simple CLI tool for quickly getting information about specific Pokémon.
Data is retrieved from pokeapi.co, and the results of all requests are cached.

## Usage

```
py dex.py <Pokémon name> [id|egg|evo]
```

The Pokémon name is case insensitive.

The `id` command (also the default if a command is omitted) prints the
National Pokédex number.

The `egg` command prints a list of the Pokémon's egg groups.

The `evo` command prints a list of the Pokémon's evolution chains, e.g.:
```
$ py dex.py onix evo
Onix --(Metal Coat on trade)--> Steelix

$ py dex.py gengar evo
Gastly --(25)--> Haunter --(on trade)--> Gengar

$ py dex.py Applin evo
Applin --(Tart Apple)--> Flapple
Applin --(Sweet Apple)--> Appletun
Applin --(Syrupy Apple)--> Dipplin --(Dragon Cheer)--> Hydrapple
```

Currently, this only shows useful information for Pokémon that evolve on level-up,
when given a consumable item (e.g. a Fire Stone), when holding an item (e.g.
Steel Coat), when knowing a particular move (e.g. Dragon Cheer), and/or on trade.