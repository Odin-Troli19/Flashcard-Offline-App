# Enhanced Flashcard App - Now with Images & Resizable Text! 🎉

An improved version of your flashcard application with powerful new features while keeping everything you loved about the original.

## ✨ What's New

### 1. **Image Support**
- Attach images to **both questions AND answers**
- Perfect for visual learning, diagrams, photos, etc.
- Images are automatically saved and managed

### 2. **Resizable Text Areas**
- **Drag the resize handle** (⋮⋮⋮) at the bottom of text boxes
- Make text areas bigger or smaller as needed
- Great for long questions or detailed answers

### 3. **Dark/Light Theme**
- Toggle between themes via `View → Toggle Theme`
- Easy on the eyes for night studying
- Theme preference is saved

### 4. **Card Tagging System**
- Add multiple tags to cards (e.g., #difficult, #review, #chapter1)
- Search by tags across all decks
- View all tags with card counts

### 5. **Advanced Search**
- Search across ALL decks at once
- Searches questions, answers, and tags
- Quick results with direct links to decks

### 6. **Study Session History**
- Track all your study sessions
- View statistics: accuracy, time spent, cards studied
- See your progress over time

### 7. **Backup & Restore**
- Create timestamped backups of all data
- Includes both cards and images
- Restore from any backup file

### 8. **Plus All Original Features!**
- Create and manage multiple decks
- Add, edit, delete cards
- Study in sequential or random order
- Import/export individual decks
- Automatic saving

## 📋 Requirements

```bash
pip install Pillow
```

**Note:** The app works without Pillow, but image features will be disabled.

## 🚀 How to Run

```bash
python flashcard_app_improved.py
```

## 📖 How to Use

### Creating Cards with Images

1. Click **"➕ Add Card"** in deck management
2. Enter your question in the **resizable text box** (drag the handle to resize!)
3. Click **"📎 Attach Image"** to add an image to the question
4. Enter your answer (also resizable!)
5. Optionally attach an image to the answer
6. Add tags separated by commas (optional)
7. Click **"💾 Save Card"**

### Editing Cards

1. Go to deck management
2. Click **"📝 Edit Cards"**
3. Select a card to edit
4. Modify text, change/remove images, update tags
5. **Drag the resize handles** to adjust text box sizes
6. Save your changes

### Studying

- **Space** - Show/hide answer
- **Right Arrow (→)** - Mark as "Knew It" and go to next card
- **Left Arrow (←)** - Mark as "Didn't Know" and go to next card
- **⏸️ End Session** - Stop studying and see results

### Searching

1. Use the search bar on the main menu, OR
2. Go to `Search → Search Cards...`
3. Enter keywords (searches questions, answers, and tags)
4. Click on results to view the deck

### Themes

- `View → Toggle Theme (Dark/Light)` to switch themes
- Your preference is automatically saved

### Backup & Restore

- `File → Backup All Data` - Creates timestamped backup
- `File → Restore from Backup` - Restore from a backup file
- Backups include both JSON data and all images

## 📁 File Structure

```
your-folder/
├── flashcard_app_improved.py  # Main application
├── flashcards_data.json        # Your deck data (auto-created)
├── flashcard_images/           # Folder for card images (auto-created)
│   ├── img_20250101_123456_1234.jpg
│   └── ...
└── flashcard_backups/          # Backup folder (auto-created)
    ├── backup_20250101_120000.json
    ├── images_20250101_120000/
    └── ...
```

## 🎨 Features Comparison

| Feature | Original | Enhanced |
|---------|----------|----------|
| Multiple decks | ✅ | ✅ |
| Add/Edit/Delete cards | ✅ | ✅ |
| Study modes | ✅ | ✅ |
| Import/Export decks | ✅ | ✅ |
| **Images on cards** | ❌ | ✅ |
| **Resizable text areas** | ❌ | ✅ |
| **Dark/Light themes** | ❌ | ✅ |
| **Card tagging** | ❌ | ✅ |
| **Search across decks** | ❌ | ✅ |
| **Study history** | ❌ | ✅ |
| **Backup/Restore** | ❌ | ✅ |

## 💡 Tips

1. **Use tags strategically**: Tag cards by difficulty, chapter, or topic for easy filtering
2. **Resize text boxes**: Drag the resize handle to make text areas comfortable for your content
3. **Attach relevant images**: Diagrams, charts, photos - perfect for visual learning
4. **Regular backups**: Use `File → Backup All Data` before major changes
5. **Dark mode for night**: Switch to dark theme for late-night study sessions
6. **Search is powerful**: It searches everywhere - questions, answers, and tags
7. **Study history**: Track your progress and see improvement over time

## 🐛 Troubleshooting

**Images not working?**
- Install Pillow: `pip install Pillow`
- Restart the application

**App won't start?**
- Make sure you have Python 3.x installed
- Check that tkinter is available (usually comes with Python)

**Lost your data?**
- Check the `flashcard_backups/` folder
- Use `File → Restore from Backup`

## 📝 Notes

- All your original deck data is compatible
- The app automatically upgrades your data structure
- Images are stored separately in the `flashcard_images/` folder
- Backups include both JSON data and images
- The original functionality remains exactly the same

## 🎓 Perfect For

- Language learning (images + text)
- Medical studies (diagrams + definitions)
- History (photos + facts)
- Science (formulas + explanations)
- Any subject that benefits from visual aids!

---

**Enjoy your enhanced flashcard experience! 📚✨**

If you need any help, the keyboard shortcuts are available under `Help → Keyboard Shortcuts`.
