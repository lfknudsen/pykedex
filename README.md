# Pykédex

A simple CLI tool for quickly getting information about specific Pokémon.
Data is retrieved from https://www.pokeapi.co, and the results of all requests are cached.

Contributions of any kind, no matter how trivial, are more than welcome, as long as they are not LLM-generated.

## Usage

```
py dex.py [-v] <Pokémon name> [id|egg|evo]
```

The Pokémon name is case insensitive.

The `id` command (also the default if a command is omitted) prints the
National Pokédex number.

The `egg` command prints a list of the Pokémon's egg groups.

The `evo` command prints a list of the Pokémon's evolution chains.

The `-v` flag will print any HTTP requests being made. Can be used to verify caching.

The following short-hand command is also supported:
```
py evo.py [-v] <Pokémon name>
```


## Examples

```
$ py dex.py onix evo
Onix --(holding Metal Coat on trade)--> Steelix

$ py dex.py haunter evo
Gastly --(at lv 25)--> Haunter --(on trade)--> Gengar

$ py dex.py Eevee evo
Eevee --(using Water Stone)-->                            Vaporeon
Eevee --(using Thunder Stone)-->                          Jolteon 
Eevee --(using Fire Stone)-->                             Flareon 
Eevee --(with happiness 160 during the day)-->            Espeon  
Eevee --(with happiness 160 during the night)-->          Umbreon 
Eevee --(in Eterna Forest)-->                             Leafeon 
Eevee --(in Pinwheel Forest)-->                           Leafeon 
Eevee --(on Route 20)-->                                  Leafeon 
Eevee --(using Leaf Stone)-->                             Leafeon 
Eevee --(on Route 217)-->                                 Glaceon 
Eevee --(on Twist Mountain)-->                            Glaceon 
Eevee --(in Frost Cavern)-->                              Glaceon 
Eevee --(using Ice Stone)-->                              Glaceon 
Eevee --(knowing a Fairy-type move with affection 2)-->   Sylveon 
Eevee --(knowing a Fairy-type move with happiness 160)--> Sylveon

$ py dex.py -v gligar evo
MAKING HTTP REQUEST TO https://pokeapi.co/api/v2/pokemon-species/gligar/
MAKING HTTP REQUEST TO https://pokeapi.co/api/v2/evolution-chain/104/
MAKING HTTP REQUEST TO https://pokeapi.co/api/v2/pokemon-species/gliscor/
MAKING HTTP REQUEST TO https://pokeapi.co/api/v2/item/razor-fang/
Gligar --(holding Razor Fang during the night)--> Gliscor

$ py dex.py -v glaceon evo
Eevee --(on Route 217)-->      Glaceon
Eevee --(on Twist Mountain)--> Glaceon
Eevee --(in Frost Cavern)-->   Glaceon
Eevee --(using Ice Stone)-->   Glaceon
```

Currently, this only shows useful information for Pokémon that evolve in one or more
of the following ways:
* at a particular level,
* when given a consumable item (e.g. a Fire Stone for Growlithe into Arcanine),
* when holding an item (e.g. Steel Coat for Onix into Steelix),
* when knowing a particular move (e.g. Dragon Cheer for Dipplin into Hydrapple),
* when knowing a move of a particular type (e.g. Fairy),
* in a particular location (e.g. Mount Lanakila),
* with high friendship (e.g. Azurill into Marill),
* with high affection,
* at a particular time of day
* on trade.


## To-Do
* Give the output colours
* Movesets
* Stats
* TM lookup
* Move lookup
* Item lookup
* Specify generation or game
* ...