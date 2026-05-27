# Pykedex

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
$ py dex.py tyranitar evo
larvitar --30--> pupitar --55--> tyranitar
```

Currently, this only shows useful information for Pokémon that evolve on level-up:
```
$ py dex.py Applin evo
applin --None--> flapple
applin --None--> appletun
applin --None--> dipplin --None--> hydrapple
```
