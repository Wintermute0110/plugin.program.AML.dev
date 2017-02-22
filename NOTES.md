## Boolean options ##

A machine has the boolean option or not.

 * Parent / Clone (integrated on filter menu)

 * Working / NonWorking (display tag)

 * BIOS / NoBIOS (display tag)

 * Coins / NoCoins (own menu `Machines (with coin slot)` and `Machines (no coin slot)`)

 * Mechanical / NonMechanical (own menu `Machines (mechanical)`)

 * CHD / NoCHD (own menu `Machines with CHDs`)

 * Sample / NoSamples (own menu `Machines with Samples`)

 * Devices / Nodevices (filtered out when making main database)


## Input data and directories ##

 Directory                  | Explanation
----------------------------|---------------------------------
`~/AML-ROMs/`               | MAME ROMs
`~/AML-CHDs/`               | MAME CHDs
`~/AML-SL-ROMs/`            | SL ROMs
`~/AML-SL-CHDs/`            | SL CHDs
`~/AML-assets/`             | All assets
`~/AML-assets/samples/`     |
`~/AML-assets/Catver.ini`   |
`~/AML-assets/Catlist.ini`  |
`~/AML-assets/Genre.ini`    |
`~/AML-assets/nplayers.ini` |

## Launching MAME machines with media types (former MESS) ##

http://www.mess.org/mess/howto

### Known media types in MAME ###

 Name      | Short name | Machine example  |
-----------|------------|------------------|
cartridge  | cart       | 32x, sms, smspal |
cassete    | cass       |                  |
floppydisk | flop       |                  |
quickload  | quick      |                  |
snapshot   | dump       |                  |
harddisk   | hard       |                  |
cdrom      | cdrm       |                  |
printer    | prin       |                  |

Machines may have more than one media type. In this case, a number is appended at the end. For
example, a machine with 2 cartriged slots has `cartridge1` and `cartridge2`.

### Cartridges ###

Most consoles have only one cartridge slot, for example `32x`.

```
<machine name="32x" sourcefile="megadriv.cpp">
...
<device type="cartridge" tag="cartslot" mandatory="1" interface="_32x_cart">
	<instance name="cartridge" briefname="cart"/>
	<extension name="32x"/>
	<extension name="bin"/>
</device>
```

Device name and its brief version can be used at command line to launch a specific program/game.

```
mame 32x -cartridge foo1.32x
mame 32x -cart foo1.32x
```

A machine may have more than one cartridge slot, for example `abc110`.

```
<machine name="abc110" sourcefile="bbc.cpp" cloneof="bbcbp" romof="bbcbp">
...
<device type="cartridge" tag="exp_rom1" interface="bbc_cart">
    <instance name="cartridge1" briefname="cart1"/>
    <extension name="bin"/>
    <extension name="rom"/>
</device>
<device type="cartridge" tag="exp_rom2" interface="bbc_cart">
    <instance name="cartridge2" briefname="cart2"/>
    <extension name="bin"/>
    <extension name="rom"/>
</device>
...
```

Launching command example.

```
mame abc110 -cart1 foo1.bin -cart2 foo2.bin
```


## Launching Software Lists ##

http://www.mess.org/mess/howto#software_lists

http://www.mess.org/mess/swlist_format

Example of machines with SL: `32x`.

```
<machine name="32x" sourcefile="megadriv.cpp">
...
    <device type="cartridge" tag="cartslot" mandatory="1" interface="_32x_cart">
		<instance name="cartridge" briefname="cart"/>
		<extension name="32x"/>
		<extension name="bin"/>
	</device>
	<slot name="cartslot">
	</slot>
	<softwarelist name="32x" status="original" filter="NTSC-U" />
</machine>
```


## Plugin URL schema ##

 Root menu                    | 1st sub          | 2nd     | 3rd    | URL                                                               |
------------------------------|------------------|---------|--------|-------------------------------------------------------------------|
Machines (with coin slot)     | Parents          | Clones  |        | ?catalog=None           &category=Machines       &parent=ROM_name |
Machines (no coin slot)       | Parents          | Clones  |        | ?catalog=None           &category=NoCoin         &parent=ROM_name |
Machines (mechanical)         | Parents          | Clones  |        | ?catalog=None           &category=Mechanical     &parent=ROM_name |
Machines (dead)               | Parents          | Clones  |        | ?catalog=None           &category=Dead           &parent=ROM_name |
Machines with CHDs            | Parents          | Clones  |        | ?catalog=None           &category=CHD            &parent=ROM_name |
Machines with Samples         | Parents          | Clones  |        | ?catalog=None           &category=Samples        &parent=ROM_name |
Machines by Category (Catver) | Category         | Parents | Clones | ?catalog=Catver         &category=Cat_name       &parent=ROM_name |
Machines by Category (Catlist)| Category         | Parents | Clones | ?catalog=Catlist        &category=Cat_name       &parent=ROM_name |
Machines by Category (Genre)  | Category         | Parents | Clones | ?catalog=Genre          &category=Cat_name       &parent=ROM_name |
Machines by Manufacturer      | Manufacturer     | Parents | Clones | ?catalog=Manufacturer   &category=Man_name       &parent=ROM_name |
Machines by Year              | Year             | Parents | Clones | ?catalog=Year           &category=Year_name      &parent=ROM_name |
Machines by Driver            | Driver           | Parents | Clones | ?catalog=Driver         &category=Driver_name    &parent=ROM_name |
Machines by Control Type      | Controls         | Parents | Clones | ?catalog=Controls       &category=Control_name   &parent=ROM_name |
Machines by Display Tag       | Display Tag      | Parents | Clones | ?catalog=Display_Tag    &category=Display_tag    &parent=ROM_name |
Machines by Display Type      | Display Type     | Parents | Clones | ?catalog=Display_Type   &category=Display_type   &parent=ROM_name |
Machines by Display Rotation  | Display Rotation | Parents | Clones | ?catalog=Display_Rotate &category=Display_rotate &parent=ROM_name |
Machines by Software List     | SoftList         | Parents | Clones | ?catalog=BySL           &category=SL_name        &parent=ROM_name |
Software Lists                | SoftList         | Parents | Clones | ?catalog=SL             &SL=SL_name                               |

## Old Index file format ##

Parent/Clone list with number of clones.

```
{
  "1942": {
    "machines": [
      "1942abl",
      "1942a",
      "1942b",
      "1942h",
      "1942p",
      "1942w"
    ],
    "num_clones": 6
  },
"1943": {
    "machines": [
      "1943bj",
      "1943ja",
      "1943b",
      "1943j",
      "1943u",
      "1943ua"
    ],
    "num_clones": 6
  }
}
```

## Old Catalog file format ##

Parent only list.
Clones are calculated on the fly: `for m_name in main_pclone_dic[parent_name]:`

``` Catalog_driver.json
{
  "1942.cpp": {
    "machines": [
      "1942"
    ],
    "num_machines": 1
  },
  "1943.cpp": {
    "machines": [
      "1943kai",
      "1943mii",
      "1943"
    ],
    "num_machines": 3
  }
}
```

## New unified catalog format ###

Supports Normal and PClone display modes.
Supports hashed database to store machine information.
Supports current big database to acces all the information.

NOTE Iterating a list is faster than iterating a dictionary 
See http://stackoverflow.com/questions/12543837/python-iterating-over-list-vs-over-dict-items-efficiency

## Implementation steps ##

1) Unify current index and catalog into just a catalog.
2) Implement Normal and PClone display modes using big database.
3) Implement `Machines hashed DB` for quick access to individual machine information on the View
   context menu.
5) Implement Normal and PClone display modes using a hashed database for maximum performance.

### Catalog_driver_parents.json ###

  1) Has a list of parents for every category and number of clones.
  2) Clone list are obtained from the main PClone dictionary on the fly when rendering a 
     Clones list.
  3) Used to render list in PClone display mode.
  4) Hashed database entry for each category that includes all parents data -> `Parents hashed DB`.
  5) To reduce number of files the `PClone hashed DB` can also be used at a performance cost
     (bigger DB, higher loading times).
  6) All clones data in -> `Machines hashed DB`.
  
``` CatalogName_driver_parents.json
{
  "1942.cpp": {
    "parents": [
      "1942":  6, # parent_name : number_of_clones
      "1946":  2
    ],
    "num_parents": 2
  },
...
}
```

### Catalog_driver_all.json ###

  1) For each category has a list of all parents and clones.
  2) Used ro render list in Normal mode.
  3) Hashed database entry for each category that includes all parents and clones 
     data -> `PClone hashed DB`.

``` CatalogName_driver_all.json
{
  "1942.cpp": {
    "machines": [
      "1942"      # Parent
      "1942abl",  # Clone
      "1942a",    # Clone
      "1942b",
      "1942h",
      "1942p",
      "1942w",
      "1932"      # Parent
    ],
    "num_machines": 6
  },
...
}
```

## Hashed machine database ###

### Parents hashed DB ###

 1) Make database name by merging catalog and category -> db_name = 'catalog' + '-' + 'category'
 2) Make MD5 hash of db_name. JSON filename is MD5.json
 3) Put all parent machine data belonging to catalog-category in JSON filename.

### PClone hashed DB ###

 1) Same as Parent hashed DB
 2) In every JSON file put all parent plus clone machine data belonging to catalog-category.

### Machines hashed DB ###

Database generation

 1) Traverse list of parents.
 2) Get hash for parent name: 1942 --> 519c84155964659375821f7ca576f095
 3) Get first two caracters of hash to compute DB filename --> 51.json
 4) In 51.json filename include parent data and all clones data.

To acess parent machine data:
 
 1) Follow same steps as in database generation.
 
To acess single clone machine data:

 1) Get parent name of clone machine.
 2) Follow same steps as in database generation.

To acess all clones machine data:

 1) Get parent name of clone machine.
 2) Follow same steps as in database generation. All clones are guaranteed to be in same
    database file as the parent.
