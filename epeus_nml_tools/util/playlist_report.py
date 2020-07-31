from uuid import uuid4
from lxml import etree
from traktor_nml_utils import TraktorCollection

collection = TraktorCollection("../../Native Instruments/Traktor 3.2.1/collection.nml")
output = "unplayed.nml"

search_playlists = [
    "Epeus/--- 2018",
    "Epeus/--- 2019",
    "Epeus/--- 2020",
]
exclude_playlists = [
    "Epeus/- Bindiism 2",
    "Epeus/- Bindiism 3",
    "Epeus/- Bindiism 4",
    "Epeus/- Bindiism 5",
]


class UnplayedPlaylist:
    def __init__(self, collection_path: str):

        self.collection_path = collection_path
        self.not_played = []
        self.played = []
        self.all_entries = []
        self.entries = {}
        self.num_all = 0
        self.num_not_played = 0
        self.num_played = 0
        self.parse_collection()

    def parse_collection(self):
        self.collection = TraktorCollection(self.collection_path)

    def get_diff(self, search_playlists, exclude_playlists):
        self.get_entries()
        self.get_played(exclude_playlists)
        self.get_not_played(search_playlists)
        self.get_counts()

    def get_playlists(self, exclude=[]):
        playlists = []
        for playlist in self.collection.playlists:
            if playlist in exclude:
                continue
            playlists.append(playlist.name)
        return playlists

    def get_entries(self):
        for entry in self.collection.entries:
            key = "{VOLUMEID}{DIR}{FILE}".format(
                **entry.xmltree.find("LOCATION").attrib
            )
            self.entries[key] = entry.xmltree

    def get_played(self, exclude_playlists):
        for playlist in self.collection.playlists:
            if playlist.name in exclude_playlists:
                for entry in playlist.entries:
                    if entry not in self.played:
                        self.played.append(entry)

    def get_not_played(self, search_playlists):
        for playlist in self.collection.playlists:
            if playlist.name in search_playlists:
                for entry in playlist.entries:
                    if entry not in self.all_entries:
                        self.all_entries.append(entry)
                    if entry not in self.played and entry not in self.not_played:
                        self.not_played.append(entry)

    def get_counts(self):
        self.num_all = len(self.all_entries)
        self.num_not_played = len(self.not_played)
        self.num_played = len(self.played)

    def create_playlist(self, name):
        # Create root structure
        nml = etree.Element("NML", **self.collection.xml_tree.getroot().attrib)
        etree.SubElement(
            nml, "HEAD", **self.collection.xml_tree.getroot().find("HEAD").attrib
        )
        etree.SubElement(nml, "MUSICFOLDERS")

        # Create the collection and entires
        collection = etree.SubElement(
            nml, "COLLECTION", ENTRIES=str(self.num_not_played)
        )
        for entry in self.not_played:
            entry_elem = self.entries[entry.xmltree.find("PRIMARYKEY").attrib["KEY"]]
            collection.append(entry_elem)

        # Create empty sets element
        etree.SubElement(nml, "SETS", ENTRIES="0")

        # Create playlist and populate with entries
        playlists = etree.SubElement(nml, "PLAYLISTS")
        folder = etree.SubElement(playlists, "NODE", TYPE="FOLDER", NAME="$ROOT")
        subnodes = etree.SubElement(folder, "SUBNODES", COUNT="1")
        node = etree.SubElement(subnodes, "NODE", NAME=name, TYPE="PLAYLIST")
        playlist = etree.SubElement(
            node,
            "PLAYLIST",
            ENTRIES=str(self.num_not_played),
            TYPE="LIST",
            UUID=uuid4().hex,
        )
        for entry in self.not_played:
            playlist.append(entry.xmltree)

        return etree.ElementTree(nml)
