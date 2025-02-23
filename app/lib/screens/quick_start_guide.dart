import 'package:flutter/material.dart';

class QuickStartGuide extends StatelessWidget {
  final VoidCallback onClose;

  const QuickStartGuide({Key? key, required this.onClose}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final guideItems = [
      {
        'icon': Icons.person,
        'color': Colors.blue,
        'title': 'Nombre del Asistente',
        'description': 'Dale un nombre único a tu asistente virtual para identificarlo fácilmente'
      },
      {
        'icon': Icons.cases_outlined,
        'color': Colors.purple,
        'title': 'Caso de Uso',
        'description': 'Describe para qué usarás el asistente. Esto ayuda a optimizar su funcionamiento'
      },
      {
        'icon': Icons.update,
        'color': Colors.green,
        'title': 'Frecuencia de Reentrenamiento',
        'description': 'Elige cada cuánto tiempo el asistente actualizará su conocimiento con nueva información'
      },
      {
        'icon': Icons.cloud_outlined,
        'color': Colors.orange,
        'title': 'Tipo de Procesamiento',
        'description': 'Elige entre procesamiento local (en tu dispositivo) o en la nube según tus necesidades de privacidad'
      },
      {
        'icon': Icons.upload_file,
        'color': Colors.red,
        'title': 'Subir Archivos',
        'description': 'Sube los archivos PDF que contienen la información que quieres que tu asistente aprenda'
      },
      {
        'icon': Icons.play_circle_outline,
        'color': Colors.indigo,
        'title': 'Entrenar Asistente',
        'description': 'Una vez configurado todo, presiona este botón para crear y entrenar tu asistente virtual'
      },
    ];

    return Dialog(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Container(
        width: double.maxFinite,
        constraints: BoxConstraints(
          maxWidth: 600,
          maxHeight: MediaQuery.of(context).size.height * 0.8,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Guía Rápida de Inicio',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  IconButton(
                    icon: Icon(Icons.close),
                    onPressed: onClose,
                  ),
                ],
              ),
            ),
            Divider(),
            Expanded(
              child: ListView.builder(
                padding: EdgeInsets.all(16),
                itemCount: guideItems.length,
                itemBuilder: (context, index) {
                  final item = guideItems[index];
                  return Card(
                    margin: EdgeInsets.only(bottom: 16),
                    elevation: 2,
                    child: InkWell(
                      borderRadius: BorderRadius.circular(8),
                      onTap: () {}, // Optional: Add specific actions for each card
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              padding: EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: item['color'] as Color,
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Icon(
                                item['icon'] as IconData,
                                color: Colors.white,
                                size: 24,
                              ),
                            ),
                            SizedBox(width: 16),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    item['title'] as String,
                                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                          fontWeight: FontWeight.bold,
                                        ),
                                  ),
                                  SizedBox(height: 4),
                                  Text(
                                    item['description'] as String,
                                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                          color: Colors.grey[600],
                                        ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}