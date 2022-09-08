## NOTES

## Rules:
1. if some part of code gets redundant it still should be saved to root in to "OLD CODE" folder. with filename "CurrentFileName_old".

### Mini Goals:
- [ ] Send message from client to server (Can do LocalHost)
- [ ] Send message from server to client (Can do LocalHost)
- [ ] Try sending message from client to client through server
  - **Note!** is not used in actual program, just a test.
- [ ] Send message to server and then from there to chat room (Can do LocalHost)
  - **Note!** Requires the completion of chat room class. (does not need to be the final version)
- [ ] Hash the messages that are sent to chat room, so that only client with password can decode the hash (MD5 hash is okay for now)


### Final Version Requirements:
- Server contains chat room admins can create.
  - Admin is privilege given to a client.
  - Only Uber Admin can give admin rights.
- Client has to log in to server when making connection to the server.
  - This should authenticate clients software version, and deny access if the software version does not with expected version.
- Log in auth sw needed.
- Client then can send messages to the chat room, those message will be displayed to all people have correctly logged in to the server.
- Server saves all messages to log files (server side) that will be deleted when chat room is deleted by admin.