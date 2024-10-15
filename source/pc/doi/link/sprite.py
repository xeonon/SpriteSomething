#pylint: disable=attribute-defined-outside-init
#pylint: disable=fixme, import-error, too-many-branches
'''
Link Sprite Specifics
'''
import itertools
import json #for reading JSON
import os   #for filesystem manipulation
import io   #for filesystem manipulation
import re
from string import ascii_uppercase, digits
from json.decoder import JSONDecodeError
from PIL import Image
from source.meta.common import common
from source.meta.classes.spritelib import SpriteParent

class Sprite(SpriteParent):
    '''
    Link Sprite Object
    '''
    def __init__(self, filename, manifest_dict, my_subpath, sprite_name=""):
        super().__init__(filename, manifest_dict, my_subpath, sprite_name)
        self.load_plugins()

        self.link_globals = {}
        self.link_globals["zap_palette"] = [
#                (  0,  0,  0),
                (  0,  0,  0),
                (208,184, 24),
                (136,112,248),
                (  0,  0,  0),
                (208,192,248),
                (  0,  0,  0),
                (208,192,248),

                (112, 88,224),
                (136,112,248),
                ( 56, 40,128),
                (136,112,248),
                ( 56, 40,128),
                ( 72, 56,144),
                (120, 48,160),
                (248,248,248)
        ]
        # FIXME: Z3DoI
        self.link_globals["yellow_mail"] = [
                # (  0,  0,  0),
                (248,248,248),
                (240,216, 64),
                (184,104, 32),
                (240,160,104),
                ( 40, 40, 40),
                (248,120,  0),
                (192, 24, 32),
                (232, 96,176),
                (171,160,  0),
                (255,242,  0),
                (171,160,  0),
                (255,242,  0),
                (224,144, 80),
                (136, 88, 40),
                (192,128,240)
        ]
        self.link_globals["sword_palette"] = [
            #blade, border, hilt
            [(248,248,248),(248,248, 72),(104,136,184)], #fighters
            [(112,144,248),(160,248,216),(168, 56, 56)], #master
            [(216, 72, 16),(248,160, 40),(104,160,248)], #tempered
            [(248,200,    0),(248,248,200),(    0,144, 72)]    #golden
        ]

    def get_representative_images(self, style):
        '''
        Generate preview image set
        '''
        return_images = []
        return_images += super().get_representative_images(style)

        if style == "crossproduct":
            return_images += self.get_tracker_images()
        elif style.lower() in ["spiffy", "hunk", "moechicken"]:
            return_images += self.get_defined_images(style.lower(), return_images)

        return return_images

    def get_tracker_images(self):
        '''
        Crossproduct Tracker Images
        '''
        return_images = []

        #cycle through mail levels
        for i,mail in enumerate(["green","blue","red","yellow","cursed"]):
            #get a container for tile lists
            tile_list = {}
            #get Bunny tile list for Stand:down to grab the bunny head
            tile_list["bunny"] = self.get_tiles_for_pose("Bunny stand","down",0,["bunny_mail"],0)
            #get Link tile list for File select for base
            tile_list["link"] = self.get_tiles_for_pose("File select","right",0,[mail + "_mail"],0)
            #get the bunny head
            bunny_head = tile_list["bunny"][2]
            #copy Link over Bunny
            tile_list["bunny"] = tile_list["link"] + []
            #set the bunny head
            tile_list["bunny"][1] = bunny_head

            #cycle through tile lists
            for tileset_id, tile_set in tile_list.items():
                #make src image from tile list
                src_img,_ = self.assemble_tiles_to_completed_image(tile_set)
                #crop out the actual pixels
                src_img = src_img.crop((5,7,21,29))
                #make a new 32x32 transparent image
                dest_img = Image.new("RGBA",(32,32))
                #paste the pixels to (7,7)
                dest_img.paste(src_img,(7,6))
                #resize using nearest neighbor to 400% because that's what Cross' tracker uses
                dest_img = dest_img.resize((32*4,32*4),Image.NEAREST)
                if mail == "cursed":
                    dest_img = dest_img.convert('LA').convert('RGBA')
                #save to disk
                filename = "tunic"
                if tileset_id == "bunny":
                    filename += "bunny"
                filename += str(i+1)
                filename += ".png"
                return_images.append((filename,dest_img))

        return return_images

    def get_defined_images(self, style, return_images):
        bgfilename = ""

        if style == "spiffy":
            bgfilename = "titlecard.png"
        elif style == "hunk":
            bgfilename = "hunk.png"
        elif style.lower() == "moechicken":
            bgfilename = "moechicken.png"

        if "sprite.name" in self.metadata and self.metadata["sprite.name"]:
            sprite_save_name = self.metadata["sprite.name"].lower()
        else:
            # FIXME: English
            sprite_save_name = "unknown"
        bgimg = Image.open(
            os.path.join(
                ".",
                "resources",
                "app",
                self.resource_subpath,
                "sheets",
                bgfilename
            )
        ).convert("RGBA")
        for i,_ in enumerate(return_images):
            img = return_images[i][1]
            pose_coords = (0, 0)
            if len(return_images[i]) > 2:
                pose_coords = tuple(return_images[i][2])
            bgimg.paste(img,pose_coords,img)
        bgimg = bgimg.resize((bgimg.size[0] * 2, bgimg.size[1] * 2), Image.NEAREST)
        return_images.append(("-".join([sprite_save_name,bgfilename]),bgimg))
        return_images = return_images[-1:]
        return return_images

    def get_alternate_tile(self, image_name, palettes):
        '''
        Get alternate tile to replace requested tile
        '''
        slugs = {}
        found_alt = ""
        for palette in palettes:
            if '_' in palette:
                slugs[
                    palette[
                        palette.rfind('_')+1:
                    ]
                ] = palette[
                    :palette.rfind('_')
                ]
        for item in ["SWORD","SHIELD"]:
            if image_name.startswith(item):
                if item.lower() in slugs:
                    found_alt = True
                    image_name = image_name.replace(
                        item,
                        slugs[item.lower()] + '_' + item.lower()
                    ) if not "none_" + item.lower() in palettes else \
                    "transparent"
        if "accessories" in slugs:
            for item in [
                "BED",
                "BOOMERANG",
                "BOW",
                "BUGNET",
                "CANE",
                "HAMMER",
                "HOOK",
                "POWDER",
                "ROD",
                "SHALLOW_WATER",
                "SHOVEL",
                "SWAGDUCK",
                "TALL_GRASS",
                "MASTER_SWORD",
                ]:
                if image_name.startswith(item):
                    found_alt = True
                    image_name = image_name.lower() if \
                        not "none_accessories" in palettes else \
                        "transparent"
            for item, default in [
                    ("ITEM","pendant"),
                    ("CRYSTAL","crystal"),
                    ("BUSH_SHADOW","main_shadow")
                ]:
                if image_name.startswith(item):
                    found_alt = True
                    image_name = default.lower() if \
                        not "none_accessories" in palettes else \
                        "transparent"
            for item in ["BUSH","BOOK"]:
                if image_name.startswith(item):
                    found_alt = True
                    image_name = image_name.lower() if \
                        not "none_accessories" in palettes else \
                        "transparent"
        if found_alt:
            return self.images[image_name] if image_name in self.images else self.images["transparent"]
        if True:
            #TODO: Track down why this function is being called without
            # spiffy button info during sprite load
            return Image.new("RGBA",(0,0),0)
        # FIXME: English
        raise AssertionError(f"Could not locate tile with name {image_name}")

    def import_cleanup(self):
        '''
        Post-import cleanup
        '''
        self.load_plugins()
        self.equipment = self.plugins.equipment_test(False)
        if hasattr(self, "images"):
            self.images["transparent"] = Image.new("RGBA",(16,16),0)
            self.images = dict(self.images,**self.equipment)

    def import_from_ROM(self, rom):
        '''
        Import Link from ROM
        '''
        author_data = self.translate_author(rom)
        self.metadata["author.name"] = author_data
        self.metadata["author.name-short"] = author_data
        pixel_data = rom.bulk_read_from_snes_address(0x108000,0x7000)       #the big Link sheet
        palette_data = rom.bulk_read_from_snes_address(0x1BD308,120)        #the palettes
        palette_data.extend(rom.bulk_read_from_snes_address(0x1BEDF5,4))    #the glove colors
        self.import_from_binary_data(pixel_data,palette_data)

    def import_from_binary_data(self,pixel_data,palette_data):
        '''
        Import imagery from binary data
        '''
        num_palettes = 5
        self.master_palette = [(0,0,0) for _ in range(0x10 * num_palettes)]     #initialize the palette
        #main palettes
        #FIXME: Z3DoI is expecting to find Yellow Mail
        converted_palette_data = [int.from_bytes(palette_data[i:i+2], byteorder='little') \
                                                            for i in range(0,len(palette_data),2)]
        for i in range(num_palettes):
            palette = common.convert_555_to_rgb(converted_palette_data[0x0F*i:0x0F*(i+1)])
            self.master_palette[0x10*i+1:0x10*(i+1)] = palette
        #glove colors
        for i in range(2):
            glove_color = common.convert_555_to_rgb(converted_palette_data[-2+i])
            self.master_palette[0x10+0x10*i] = glove_color

        palette_block = Image.new('RGBA',(8,num_palettes * 2),0)
        is_z3link = os.path.join("zelda3","link") in self.filename or self.internal_name == "link"
        is_doi = True #is_z3link and len(self.master_palette) == 80
        pblock_data = self.master_palette
        if is_z3link:
            # print("Is Z3Link")
            null_palette = [(0,0,0,0) for _ in range(0x10)]
            if not is_doi:
                # print("Is NOT DoI")
                # Get G B R
                gbr_mails = self.master_palette[0x10 * 0:0x10 * 3]
                # Get Bunny
                bun_mail = self.master_palette[0x10 * 3:0x10 * 4]
                # Y G B R Bun
                pblock_data = [
                    *null_palette,
                    *gbr_mails,
                    *bun_mail
                ]
            else:
                self.subtype = "doi"
                # Get G B R
                gbr_mails = self.master_palette[:0x10 * 3]
                # Get Yellow
                y_mail = self.master_palette[0x10 * 3:0x10 * 4]
                # Get Bunny
                bun_mail = self.master_palette[0x10 * 4:0x10 * 5]
                # Y G B R Bun
                pblock_data = [
                    *y_mail,
                    *gbr_mails,
                    *bun_mail
                ]
        pblock_mod = len(pblock_data) % 16
        # print("Import from Binary")
        # print("Set Palette Block")
        # print("Pre-Mod:",len(pblock_data),pblock_mod)
        if pblock_mod:
            # print("Modding")
            pblock_data = pblock_data[:len(pblock_data) - (pblock_mod)]
        # print("Post-Mod:",len(pblock_data))
        palette_block.putdata(pblock_data)

        self.images = {}
        self.images["palette_block"] = palette_block

        for i,row in enumerate(itertools.chain(ascii_uppercase, ["AA","AB"])):
            for column in range(8):
                this_image = Image.new("P",(16,16),0)
                image_name = f"{row}{column}"
                if image_name == "AB7":
                    image_name = "null_block"
                for offset, position in [
                    (0x0000,(0,0)),
                    (0x0020,(8,0)),
                    (0x0200,(0,8)),
                    (0x0220,(8,8))
                ]:
                    read_pointer = 0x400*i+0x40*column+offset
                    raw_tile = pixel_data[read_pointer:read_pointer+0x20]
                    pastable_tile = common.image_from_bitplanes(raw_tile)
                    if pastable_tile:
                        this_image.paste(pastable_tile,position)
                    else:
                        print(f"🟡WARNING: {image_name}:[{offset}:{position}] not loadable")
                        #FIXME: Z3DoI, probably DoI if these are having issues
                        #Bottom row of tiles is broke
                        #This affects Attack (down & up), Dash (down) and crystalGet
                        # self.subtype = "doi"
                self.images[image_name] = this_image

    def get_palette(self, palettes, default_range=[], frame_number=0):
        '''
        Get palette based on input strings and frame number
        '''
        palette_indices = None
        this_palette = []
        range_end = 0x10
        if "gloves" in palettes:
            # print("Gloves Palette")
            range_end = 2 + 1
        for i in range(1,range_end):
            this_palette.append((0,0,0))

        if "zap_mail" in palettes:
            # print("Zap Palette from Globals")
            this_palette = self.link_globals["zap_palette"]
        elif "gloves" in palettes:
            # print("Gloves Palette")
            palette_indices = [0x10,0x20]
        else:
            #start with green mail and modify it as needed
            # print("Green Mail")
            palette_indices = list(range(1,range_end))
            for i,_ in enumerate(palette_indices):

                if palette_indices[i] == 0x0D:
                    if "power_gloves" in palettes:
                        # print("Power Gloves")
                        palette_indices[i] = 0x10
                    elif "titan_gloves" in palettes:
                        # print("Titan Gloves")
                        palette_indices[i] = 0x20

                if palette_indices[i] in range(0,range_end):
                    if "blue_mail" in palettes:
                        #Blue Mail
                        #skip to second row
                        # print("Blue Mail")
                        row = 2
                        palette_indices[i] += range_end * (row-1)
                    elif "red_mail" in palettes:
                        #Red Mail
                        #skip to third row
                        # print("Red Mail")
                        row = 3
                        palette_indices[i] += range_end * (row-1)
                    elif "yellow_mail" in palettes:
                        #FIXME: Z3DoI
                        #Yellow Mail
                        #skip to fourth row
                        # print("Yellow Mail")
                        row = 4
                        palette_indices[i] += range_end * (row-1)
                    elif "bunny_mail" in palettes:
                        #FIXME: Z3DoI
                        #Bunny Mail
                        #skip to fourth row; fifth if DoI
                        # print("Bunny Mail")
                        row = 5 if self.subtype == "doi" else 4
                        palette_indices[i] += range_end * (row-1)
        # print("DoI:",self.subtype == "doi")
        # print("Master Palette:")
        # n_cols = 16
        # for i in range(0, len(self.master_palette), n_cols):
        #     print(*self.master_palette[i:i+n_cols])
        # print("Palette Indices:",len(palette_indices),palette_indices)
        # print("Initialized Palette:",len(this_palette),this_palette)
        #FIXME: Z3DoI
        if "yellow_mail" in palettes:
            # print("Yellow Mail from Globals")
            this_palette = self.link_globals["yellow_mail"]
        if palette_indices:
            for i,_ in enumerate(palette_indices):
                if palette_indices[i] <= len(self.master_palette):
                    this_palette[i] = self.master_palette[palette_indices[i]]
        # print("New Palette:",len(this_palette),this_palette)
        # print("")
        return this_palette

    def get_binary_sprite_sheet(self):
        '''
        Get binary sprite sheet
        '''
        top_half_of_rows = bytearray()
        bottom_half_of_rows = bytearray()

        # 28 rows, 8 columns
        for image_name in [
            f"{row}{column}" for row in itertools.chain(
                ascii_uppercase,
                ["AA","AB"]
            )
            for column in range(8)]:
            image_name = image_name if image_name != "AB7" else "transparent"
            image = self.images[image_name]
            image.name = image_name
            raw_image = common.convert_to_4bpp(
                image,
                (0,0),
                (0,0,image.size[0],image.size[1]),
                None
            )
            top_half_of_rows += bytes(raw_image[:0x40])
            bottom_half_of_rows += bytes(raw_image[0x40:])

        return bytes(b for row_offset in range(0,len(top_half_of_rows),0x200) \
                         for b in top_half_of_rows[
                            row_offset:row_offset+0x200
                        ]+
                        bottom_half_of_rows[
                            row_offset:row_offset+0x200
                        ]
                    )

    def get_binary_palettes(self):
        '''
        Get binary palettes
        '''
        raw_palette_data = bytearray()
        # G B R
        gbr_mails = self.master_palette[:0x10 * 3]
        # Collect Yellow
        y_mail = []
        # Collect Bunny
        bun_mail = self.master_palette[0x10 * 3:0x10 * 4]
        if self.subtype == "doi":
            y_mail = bun_mail
            bun_mail = self.master_palette[0x10 * 4:]
        # G B R Y Bun
        bin_palettes = [*gbr_mails, *y_mail, *bun_mail]
        colors_555 = common.convert_to_555(bin_palettes)
        # n = 16
        # for i, e in enumerate(colors_555, 1):
        #     print("0x"+hex(e).upper()[2:].rjust(4,"0"), ["", "\n"][i % n == 0], end="")

        # Mail and bunny palettes
        palettes = int(len(bin_palettes) / 0x10)
        raw_palette_data.extend(
            itertools.chain.from_iterable(
                [
                    common.as_u16(
                        c
                    )
                    for i in range(palettes)
                    for c in colors_555[
                        0x10*i+1:0x10*i+0x10
                    ]
                ]
            )
        )

        # Glove colors
        raw_palette_data.extend(
            itertools.chain.from_iterable(
                [
                    common.as_u16(
                        colors_555[0x10*i+0x10]
                    )
                    for i in range(2)
                ]
            )
        )

        return raw_palette_data
