// lib/screens/chatbot_list_screen.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/chatbot_provider.dart';
import '../widgets/chatbot_card.dart';
import 'add_chatbot_screen.dart';
import 'chatbot_chat_screen.dart';
import '../models/chatbot.dart';

class ChatbotListScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final chatbotProvider = Provider.of<ChatbotProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: Text('SoftIA'),
      ),
      body: chatbotProvider.chatbots.isEmpty
          ? Center(
              child: Text('No hay asistentes virtuales creados aún, presiona el botón de abajo para agregar uno'),
            )
          : ListView.builder(
              itemCount: chatbotProvider.chatbots.length,
              itemBuilder: (context, index) {
                Chatbot chatbot = chatbotProvider.chatbots[index];
                return ChatbotCard(
                  chatbot: chatbot,
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => ChatbotChatScreen(chatbot: chatbot),
                      ),
                    );
                  },
                  onDelete: () async {
                    bool confirm = await showDialog(
                      context: context,
                      builder: (context) => AlertDialog(
                        title: Text('Borrar asistente virtual'),
                        content: Text('Estas seguro que querés borrar el asistente "${chatbot.name}"?'),
                        actions: [
                          TextButton(
                            onPressed: () => Navigator.pop(context, false),
                            child: Text('Cancelar'),
                          ),
                          TextButton(
                            onPressed: () => Navigator.pop(context, true),
                            child: Text('Eliminar'),
                          ),
                        ],
                      ),
                    );
                    if (confirm) {
                      await chatbotProvider.removeChatbot(chatbot.id);
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('Asistente Eliminado')),
                      );
                    }
                  },
                );
              },
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => AddChatbotScreen()),
          );
        },
        child: Icon(Icons.add),
        tooltip: 'Agregar Asistente Virtual',
      ),
    );
  }
}
