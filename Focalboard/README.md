# Focalboard

## Running in Docker

``` sh
docker run -it -p 80:8000 mattermost/focalboard
```

## My thought

This tool is similar to the data view of Notion. Data items are captured as cards. These cards can contain additional blocks of content and can be tagged with additional properties. These cards can be displayed in different ways, called views.

A few concerns that I have about this tool:

- It is no longer maintained by the organisation
- The docker instruction is quite sparse. I will need to spend more effort if I want to set up a whole stack and back it up (there is no details regarding the volume being used)
- There is no Gantt view
- The act of adding a task to the board does not seem straight forward enough to be used by my colleagues
