using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System;

public class Ai_Listener1 : MonoBehaviour  // ? Inherit MonoBehaviour
{
    Animator anim;
    TcpListener server;

    void Start()
    {
        anim = GetComponent<Animator>();  // ? Ensure this is inside a MonoBehaviour class

        server = new TcpListener(IPAddress.Any, 5000);
        server.Start();
        server.BeginAcceptTcpClient(OnClientConnect, null);
    }

    void OnClientConnect(IAsyncResult ar)
    {
        TcpClient client = server.EndAcceptTcpClient(ar);
        NetworkStream stream = client.GetStream();
        byte[] buffer = new byte[client.ReceiveBufferSize];
        int bytesRead = stream.Read(buffer, 0, buffer.Length);
        string message = Encoding.ASCII.GetString(buffer, 0, bytesRead);

        if (message == "start_speaking")
            anim.SetBool("isSpeaking", true);
        else if (message == "stop_speaking")
            anim.SetBool("isSpeaking", false);

        client.Close();
        server.BeginAcceptTcpClient(OnClientConnect, null);
    }
}
