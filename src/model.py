"""
This script contains the code for modelling the different type of artworks.
"""

from path import DATA_PATH

class Artwork:
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-few-public-methods
    # pylint: disable=too-many-arguments
    """
    This class represent a kind of artwork among the following:
    - Manga
    - Novel
    - Manhwa
    - Anime
    There might be over but those are the main ones.
    """

    def __init__(
        self,
        name=None,
        art_type=None,
        status=None,
        date=None,
        genres=None,
        score=None,
        n_members=None,
        rank=None,
        popularity=None,
        synopsis=None,
        image=None,
        quantity=None):
        """
        Constructor for the class Artwork with the following parameters:
        - art_type: The type (Anime, Manhwa, ...)
        - status: The status (Ongoing, Finished, ...)
        - date: The publishing date or airing.
        - genres: The genre (Shonen, Action, Adventure, ...)
        - score: The mean rating giving by users (between 0 and 10)
        - n_members: The number of users
        - rank: The computed rank
        - popularity: The rank of the artwork based on its number of users
        - synopsis: A sum up of the artwork
        - image: A link for the image
        """
        self.name_ = name

        self.type_ = art_type

        self.status_ = status
        self.check_status()

        self.date_ = date
        self.check_date()

        self.genres_ = genres
        self.check_genres()

        self.score_ = score
        self.check_score()

        self.n_members_ = n_members
        self.check_n_members()

        self.rank_ = rank
        self.check_rank()

        self.popularity_ = popularity
        self.check_popularity()

        self.synopsis_ = synopsis
        self.check_synopsis()

        self.image_ = image

        self.quantity_ = quantity
        self.check_quantity()

    def __str__(self):
        string = "Artwork(\n"
        string += "  name = {},\n".format(self.name_)
        string += "  type = {},\n".format(self.type_)
        string += "  status = {},\n".format(self.status_)
        string += "  date = {},\n".format(self.date_)
        string += "  genres = {},\n".format(self.genres_)
        string += "  quantity = {}\n".format(self.quantity_)
        string += "  score = {},\n".format(self.score_)
        string += "  n_members = {},\n".format(self.n_members_)
        string += "  rank = {},\n".format(self.rank_)
        string += "  popularity = {},\n".format(self.popularity_)
        string += "  image = {}\n".format(self.image_)
        string += ")"

        return string

    def check_score(self):
        """
        This method checks the score and put it the right way if it is in the
        wrong format.
        Good format: "9.71", "3.23", "5.32", "N/A"
        """
        self.score_ = self.score_ if len(self.score_) <= 4 else "N/A"

    def check_n_members(self):
        """
        This method checks the number of members and put it the right way if it is in the
        wrong format.
        """
        if isinstance(self.n_members_, int):
            return

        if isinstance(self.n_members_, str):
            # Delete the commas
            self.n_members_ = processing_hash_integer(self.n_members_)

    def check_popularity(self):
        """
        This method checks the popularity and put it the right way if it is in the
        wrong format.
        """
        if isinstance(self.popularity_, int):
            return

        if isinstance(self.popularity_, str):
            self.popularity_ = processing_hash_integer(self.popularity_)

    def check_rank(self):
        """
        This method checks the rank and put it the right way if it is in the
        wrong format.
        """
        if isinstance(self.rank_, int):
            return

        if isinstance(self.rank_, str):
            self.rank_ = processing_hash_integer(self.rank_)

    def check_genres(self):
        """
        This method checks the genres and put it the right way if it is in the
        wrong format.
        """
        if isinstance(self.genres_, list):
            self.genres_ = ', '.join(self.genres_)

    def check_quantity(self):
        """
        This method checks the quantity and put it the right way if it is in the
        wrong format.
        """
        if isinstance(self.quantity_, int):
            return

        if isinstance(self.quantity_, str):
            self.quantity_ = extract_integer(self.quantity_)

    def check_status(self):
        """
        This method checks the status and put it the right way if it is in the
        wrong format.
        """
        if self.status_ is None:
            return

        self.status_ = processing_line_break_relevant(self.status_)

    def check_date(self):
        """
        This method checks the date and put it the right way if it is in the
        wrong format.
        """
        if self.date_ is None:
            return

        self.date_ = processing_line_break_relevant(self.date_)

    def check_synopsis(self):
        """
        This method checks the synopsis and put it the right way if it is in the
        wrong format.
        """
        return self.synopsis_.replace("\n", "")

    def to_csv(self):
        """
        This method return the artwork in the form of a csv line.
        """
        vName = self.name_ if self.name_ is not None else "N/A"
        vType = self.type_ if self.type_ is not None else "N/A"
        vStatus = self.status_ if self.status_ is not None else "N/A"
        vDate = self.date_ if self.date_ is not None else "N/A"
        vGenres = self.genres_ if self.genres_ is not None else "N/A"
        vScore = str(self.score_) if self.score_ is not None else "N/A"
        vMembers = str(self.n_members_) if self.n_members_ is not None else "N/A"
        vRank = str(self.rank_) if self.rank_ is not None else "N/A"
        vPopularity = str(self.popularity_) if self.popularity_ is not None else "N/A"
        vImage = self.image_ if self.image_ is not None else "N/A"
        vQuantity = str(self.quantity_) if self.quantity_ is not None else "N/A"
        return ", ".join([surround_quotes(vName), surround_quotes(vType),
        surround_quotes(vStatus), surround_quotes(vDate),
        surround_quotes(vGenres), surround_quotes(vScore),
        surround_quotes(vMembers), surround_quotes(vRank),
        surround_quotes(vPopularity), surround_quotes(vImage),
        surround_quotes(vQuantity)])

    @staticmethod
    def csv_header(path=DATA_PATH):
        """
        This method write the list of features of the csv file.
        """
        return ", ".join(["name", "type", "status", "date", "genres", "score",
        "members", "rank", "popularity", "image",
        "quantity"])

def extract_integer(string):
    """
    Extract the first detected integer from a string.
    Return an integer if foud otherwise 'N/A'.
    """
    integer = "N/A"
    for element in string.split():
        if element.isdigit():
            integer = int(element)
            break
    return integer

def delete_hash(string):
    """
    Replace every hash # symbol in the string with nothing.
    """
    return string.replace("#", "")

def processing_hash_integer(string):
    """
    Call the delete_hash function then extract_integer over the given string.
    """
    return extract_integer(delete_hash(string))

def delete_line_break(string):
    """
    Replace every line break symbol in the string with nothing.
    """
    return string.replace("\n", "")

def extract_relevant(string):
    """
    Extract the relevant part of a string.
    Example: "Aired: 2003" -> "2003"
    """
    return "N/A" if len(string.split(":")) <= 1 else string.split(":")[1]

def processing_line_break_relevant(string):
    """
    Call the delete_line_break function then extract_relevant over the given string
    and delete the leading and ending spaces.
    """
    return extract_relevant(delete_line_break(string)).strip()

def surround_quotes(string):
    """
    Add the " character around the string.
    """
    return '"{}"'.format(string)
