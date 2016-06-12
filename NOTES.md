## Boolean options ##

 * Parent / Clone (integrated on menu)

 * Working / NonWorking (display option)

 * Coins / NoCoins (own menu)

 * Mechanical / NonMechanical (own menu)
 
 * CHD / NoCHD (display option)
 
 * BIOS / NoBIOS (display option)
 
 * Sample / NoSamples (display option)
 
 * Vertical / Horizontal (own menu)

## Main menu ##

       Root menu           | 1st submenu  | 2nd submenu | 3rd submenu | URL                                                                  |
---------------------------|--------------|-------------|-------------|----------------------------------------------------------------------|
Machines with coin slot    | Parents      | Clones      |             | ?root=Machines     &parent=<ROM_name>                                |
Machines with no coin slot | Parents      | Clones      |             | ?root=NoCoin       &parent=<ROM_name>                                |
Mechanical Machines        | Parents      | Clones      |             | ?root=Mechanical   &parent=<ROM_name>                                |
Machines by Manufacturer   | Manufacturer | Parents     | Clones      | ?root=Manufacturer &manufacturer=<Man_name>        &parent=<ROM_name>|
Machines by Year           | Year         | Parents     | Clones      | ?root=Year         &year=<Year_name>               &parent=<ROM_name>|
Machines by Driver         | Driver       | Parents     | Clones      | ?root=Driver       &driver=<Driver_name>           &parent=<ROM_name>|
Machines by Control        | Controls     | Parents     | Clones      | ?root=Controls     &control=<Control_name>         &parent=<ROM_name>|
Machines by Orientation    | Orientation  | Parents     | Clones      | ?root=Orientation  &orientation=<Orientation_name> &parent=<ROM_name>|
Software Lists             | Machine      | Parents     | Clones      | ?root=SL           &SL=<SL_name>                   &parent=<ROM_name>|


```
?                                                         URL_ROOT
?command=<command_name>                                   URL_COMMAND
?command=<command_name> &mame_args=<args>                 URL_COMMAND
?root=Machines                                            URL_LIST
?root=Machines &parent=<ROM_name>                         URL_LIST_CLONES

?root=SL                                                  URL_LIST
?root=SL       &sl=<SL_name>                              URL_CATEGORY_ITEM_LIST
?root=SL       &sl=<SL_name>      &cat_parent=<ROM_name>  URL_CATEGORY_ITEM_CLONES_LIST
```
