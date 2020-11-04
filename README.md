# honkuru
A Python based peer-to-peer text chat application using sockets.  
*Note: it's still too buggy to be useful for anything.*

### How it works
The first one, executing the program, will automatically start hosting a server.  
Everyone, who connects after that, will only connect as a client. But will receive information about who is connected. 
If the current server owner decides to disconnect, the oldest connected client will start hosting a server and all
clients will look for the Server on that connection. If they won't find it, the next one will host the server 
and so forth. 

### Dependencies
The only Dependency is `prompt_toolkit` for the tui. 

## Usage
Fill your config file accordingly:  
```
[server]  
port = 7950  
ip = 192.168.178.2  
```

port is the port all clients will connect on. I arbitrarily decided on 7950 for honkuru as the default.  
The ip is usually your local IP. Keep in mind, that you have to be able to host a server on that IP.  

#### Commands
Commands are typed in with a leading `!`.  
So you can display the help message with `!help`.  
Currently you can only change the current color theme with `!theme`. It will display all available ones.  
But obviously the green one is the best one and can be activated with `!theme dakes`. (There aren't many choices atm)  
To disconnect type `!disconnect`.  

#### flags
`-v, --verbose`: activate verbose printing  
`-s, --server`: start in server only mode.  Won't start a client or ui.  
`-h, --help`: help message


