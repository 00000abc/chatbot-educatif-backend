from django.contrib import admin
from .models import UserProfile, Conversation, Message

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Administration des profils utilisateurs"""
    list_display = ('user', 'phone', 'class_level', 'created_at')
    list_filter = ('class_level', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone')
    readonly_fields = ('created_at',)

class MessageInline(admin.TabularInline):
    """Afficher les messages dans la page de conversation"""
    model = Message
    extra = 0
    readonly_fields = ('timestamp', 'is_user', 'content', 'class_level', 'subject')
    can_delete = False

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Administration des conversations"""
    list_display = ('id', 'user', 'created_at', 'updated_at', 'message_count')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [MessageInline]
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Nombre de messages'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Administration des messages"""
    list_display = ('id', 'conversation', 'is_user_display', 'content_preview', 'timestamp')
    list_filter = ('is_user', 'timestamp', 'class_level', 'subject')
    search_fields = ('content',)
    readonly_fields = ('timestamp',)
    
    def is_user_display(self, obj):
        return '👤 User' if obj.is_user else '🤖 AI'
    is_user_display.short_description = 'Auteur'
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Contenu'