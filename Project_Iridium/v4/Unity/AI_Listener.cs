using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;

public class AI_Listener : MonoBehaviour

{
    Animator anim;
    TcpListener server;

    void Start()
    {
        anim = GetComponent<Animator>();
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
