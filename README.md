# Punch Your Friend

A pixel party game. Whoever creates a room plays **我** and dodges; everyone who opens the invite link is a **兄弟** and throws punches from above.

**Play:** https://seasong11.github.io/punch-your-friend/

- Open the page to create a room, then press **Copy invite link** and send it to friends.
- No accounts. Players connect browser-to-browser (WebRTC via PeerJS), with the host's browser as the hub, so the room lasts while the host keeps the tab open.
- Some strict networks block browser-to-browser connections; mobile data usually works.

Everything lives in `index.html`.
