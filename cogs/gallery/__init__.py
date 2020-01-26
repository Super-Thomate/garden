from .gallery import Gallery

try:  # check if BeautifulSoup4 is installed
  from bs4 import BeautifulSoup

  soupAvailable = True
except:
  soupAvailable = False


def setup(bot):
  if soupAvailable:
    bot.add_cog(Gallery(bot))
  else:
    raise RuntimeError("You need to run `python3 -m pip install -U beautifulsoup4`")
