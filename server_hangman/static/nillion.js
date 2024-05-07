async function getUserKeyFromSnap() {
    const nillionSnapId = "npm:nillion-user-key-manager";
    if (window.ethereum) {
      try {
        // Request permission to connect to the Snap.
        await window.ethereum.request({
          method: "wallet_requestSnaps",
          params: {
            [nillionSnapId]: {},
          },
        });
  
        // Invoke the 'read_user_key' method of the Snap
        const response = await window?.ethereum?.request({
          method: "wallet_invokeSnap",
          params: {
            snapId: nillionSnapId,
            request: { method: "read_user_key" },
          },
        });
  
        return {
          user_key: response?.user_key || null,
          connectedToSnap: true,
          message: ""
        };
      } catch (error) {
        console.error("Error interacting with Snap:", error);
        return {
          user_key: null,
          connectedToSnap: false,
          message: error
        };
      }
    } else {
      // Handle case where window.ethereum doesn't exist 
      console.error("Ethereum provider not found");    
      return { 
        user_key: null, 
        connectedToSnap: false, 
        message: "Ethereum provider not found" 
      };
    }
  }


document.addEventListener('DOMContentLoaded', async function () {
    r = await getUserKeyFromSnap()
    console.log(r)
    
});
