# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserTaleVariable'
        db.create_table(u'Teller_usertalevariable', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='variables', to=orm['Teller.Profile'])),
            ('tale_variable', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_values', to=orm['Teller.TaleVariable'])),
            ('value', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'Teller', ['UserTaleVariable'])

        # Adding model 'TaleVariable'
        db.create_table(u'Teller_talevariable', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tale', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Teller.Tale'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('default_value', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'Teller', ['TaleVariable'])


    def backwards(self, orm):
        # Deleting model 'UserTaleVariable'
        db.delete_table(u'Teller_usertalevariable')

        # Deleting model 'TaleVariable'
        db.delete_table(u'Teller_talevariable')


    models = {
        u'Teller.language': {
            'Meta': {'object_name': 'Language'},
            'code': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '4'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'Teller.profile': {
            'Meta': {'object_name': 'Profile'},
            'followed_users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['Teller.Profile']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'selected_links': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['Teller.TaleLink']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'Teller.rating': {
            'Meta': {'object_name': 'Rating'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 2, 14, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '2', 'decimal_places': '1'}),
            'tale': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ratings'", 'to': u"orm['Teller.Tale']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ratings'", 'to': u"orm['Teller.Profile']"})
        },
        u'Teller.tale': {
            'Meta': {'object_name': 'Tale'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_poll_tale': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['Teller.Language']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'overall_rating': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '3', 'decimal_places': '2'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '150'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tales'", 'to': u"orm['Teller.Profile']"})
        },
        u'Teller.talelink': {
            'Meta': {'object_name': 'TaleLink'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'entrances'", 'null': 'True', 'to': u"orm['Teller.TalePart']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'choices'", 'to': u"orm['Teller.TalePart']"}),
            'tale': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['Teller.Tale']"})
        },
        u'Teller.talepart': {
            'Meta': {'object_name': 'TalePart'},
            'content': ('ckeditor.fields.RichTextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_start': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'poll_end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'tale': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['Teller.Tale']"})
        },
        u'Teller.talevariable': {
            'Meta': {'object_name': 'TaleVariable'},
            'default_value': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tale': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['Teller.Tale']"})
        },
        u'Teller.usertalevariable': {
            'Meta': {'object_name': 'UserTaleVariable'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tale_variable': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_values'", 'to': u"orm['Teller.TaleVariable']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'variables'", 'to': u"orm['Teller.Profile']"}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['Teller']