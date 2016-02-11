testResponse = {
  length: 10,
  top_topics: [
    {name: "Zamorak",   topic_id:  1, number: 3,},
    {name: "Saradomin", topic_id:  2, number: 3,},
    {name: "Guthix",    topic_id:  3, number: 3,},
    {name: "Armadyl",   topic_id:  4, number: 3,},
    {name: "Seren",     topic_id:  5, number: 3,},
    {name: "Bandos",    topic_id:  6, number: 3,},
    {name: "Icthlarin", topic_id:  8, number: 3,},
    {name: "Amascut",   topic_id:  9, number: 3,},
    {name: "Elidinis",  topic_id: 10, number: 3,},
    {name: "Scabaras",  topic_id: 11, number: 3,},
    {name: "Zaros",     topic_id: 12, number: 3,},
    {name: "Marimbo",   topic_id: 13, number: 3,},
    {name: "Jas",       topic_id: 14, number: 3,},
    {name: "Bik",       topic_id: 15, number: 3,},
    {name: "Mah",       topic_id: 16, number: 3,},
    {name: "Brassica Prime", topic_id: 17, number: 3,},
  ],
}

d3.select("#input-topic").on "keydown", ->
  e = d3.event
  if e.which == 13 or e.which == 10
    e.preventDefault()
    newTopic d3.select(this).text()
.on "click", -> d3.select(this).text("")

newTopic = (topic) ->
  console.log("<Things happen to #{topic}>")

  request = JSON.stringify { search_phrase: topic, limit: 10 }

  d3.json "http://localhost:5000/top_topics_by_search_phrase/"
    .header "Content-Type", "application/json"
    .post request, (error, json) ->
      if error?
        console.log error
        response = testResponse
      else
        response = json

      print_messages topic
      loadTopics d3.shuffle response.top_topics

loadTopics = (topics) ->
  data = d3.select "#topics"
           .selectAll "li"
           .data topics

  btns = data.enter()
      .append "li"

  data.style "opacity", 0
      .text (topic) -> topic.name
      .transition()
      .delay (topic, i) -> i * 50
      .style "opacity", 1
      .each "end", ->
        d3.select this
          .on "click", (topic) ->
              d3.select "#input-topic"
                .text topic.name
              newTopic topic.name

  data.exit()
      .transition()
      .style "opacity", 0
      .remove()
