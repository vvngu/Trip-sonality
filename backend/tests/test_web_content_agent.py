import asyncio
from backend.agents.web_content_agent import web_content_agent

sample_input = {
  "extracted": [
    {
      "title": "18 Ghibli Things to Do in Tokyo - Erika's Travelventures",
      "url": "https://www.erikastravelventures.com/ghibli-things-to-do-in-tokyo/",
      "content": "Tokyo has a number of unmissable Ghibli-themed things to do including visiting the world\u2019s only Ghibli Museum, shopping for Ghibli gifts and souvenirs, and visiting locations that inspired Hayao Miyazaki and Studio Ghibli\u2019s creative process. Hotel Gajoen is one of three stops on this\u00a0Studio Ghibli tour of Tokyo\u00a0which includes tickets to the Ghibli Museum in Mitaka, Tokyo. This museum showcases traditional Japanese architecture and homes that will make visitors feel like they\u2019ve stepped back in time (and into a Studio Ghibli movie!) Elements that movie fans might recognize include\u00a0the onsen town where Chihiro\u2019s parents turn into pigs in\u00a0Spirited Away, and the village homes visited by Mei and Satsuki in\u00a0My Neighbor Totoro."
    },
    {
      "title": "A Film Lovers Guide to Tokyo - ELFS Japan",
      "url": "https://elfsjapan.com/blog/a-film-lovers-guide-to-tokyo/",
      "content": "Visit Gonpachi Restaurant. Babel. Womb nightclub is one of the largest and most popular clubs in Tokyo. It was also in a scene from a movie. If clubs are your thing, you should check it out! Visit Womb Nightclub. Anime Locations. Believe it or not a lot of the locations that crop up in anime movies are taken more or less directly from real life"
    },
    {
      "title": "Ghibli lover's guide to Tokyo: 8 best things to do for Ghibli fans",
      "url": "https://www.timeout.com/tokyo/things-to-do/studio-ghibli-guide-to-tokyo",
      "content": "The Ghibli Museum is just the start \u2013 here are the best Ghibli-related attractions, shops, cafe\u0301s and parks in Tokyo You might not encounter a giant tanuki or travel in a floating castle, but Tokyo has plenty to offer\u00a0for the die-hard Studio Ghibli fan\u00a0\u2013 from the inspirations behind popular films like \u2018Spirited Away\u2019 and \u2018My Neighbor Totoro\u2019 to authentic souvenir shopping. The Setagaya Daita location (Kichijoji is takeout-only) has an upstairs caf\u00e9 with stuffed Totoro and other Ghibli decorations that make you feel like you\u2019re in one of the studio\u2019s wholesome films. There\u2019s a seaside train station in Ehime and an old Tokyo shop that may have inspired Studio Ghibli's 'Spirited Away' 10 best Studio Ghibli films"
    },
    {
      "title": "Studio Ghibli Things To Do In Tokyo, Japan 2024 Guide + Photos",
      "url": "https://www.planmyjapan.com/studio-ghibli-tokyo-japan/",
      "content": "From edible My Neighbour Totoro cream-puffs to Studio Ghibli shops (Donguri Republic), Ghibli museums to day-trips, there are superb Studio Ghibli things to do in Tokyo to suit all tastes and budgets (some attractions are free too).. As 'The Wind Rises', be sure to check out these best Studio Ghibli activities and things to do in Tokyo, Japan:"
    }
  ]
}

async def test_web_content_agent():
    result = await web_content_agent.run(task=f"Extract real-world locations:\n{sample_input}")
    print(result.messages[-1].content)

if __name__ == "__main__":
    asyncio.run(test_web_content_agent())
