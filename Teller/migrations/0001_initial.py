# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table(u'Teller_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=25)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=150)),
        ))
        db.send_create_signal(u'Teller', ['User'])

        # Adding M2M table for field selected_links on 'User'
        m2m_table_name = db.shorten_name(u'Teller_user_selected_links')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'Teller.user'], null=False)),
            ('talelink', models.ForeignKey(orm[u'Teller.talelink'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_id', 'talelink_id'])

        # Adding model 'Tale'
        db.create_table(u'Teller_tale', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tales', to=orm['Teller.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Teller.Language'])),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=150)),
        ))
        db.send_create_signal(u'Teller', ['Tale'])

        # Adding model 'TalePart'
        db.create_table(u'Teller_talepart', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tale', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Teller.Tale'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('content', self.gf('ckeditor.fields.RichTextField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')()),
            ('poll_end_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=150)),
        ))
        db.send_create_signal(u'Teller', ['TalePart'])

        # Adding model 'TaleLink'
        db.create_table(u'Teller_talelink', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(related_name='choices', to=orm['Teller.TalePart'])),
            ('destination', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='entrances', null=True, to=orm['Teller.TalePart'])),
            ('action', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'Teller', ['TaleLink'])

        # Adding model 'Language'
        db.create_table(u'Teller_language', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('code', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=4)),
        ))
        db.send_create_signal(u'Teller', ['Language'])


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'Teller_user')

        # Removing M2M table for field selected_links on 'User'
        db.delete_table(db.shorten_name(u'Teller_user_selected_links'))

        # Deleting model 'Tale'
        db.delete_table(u'Teller_tale')

        # Deleting model 'TalePart'
        db.delete_table(u'Teller_talepart')

        # Deleting model 'TaleLink'
        db.delete_table(u'Teller_talelink')

        # Deleting model 'Language'
        db.delete_table(u'Teller_language')


    models = {
        u'Teller.language': {
            'Meta': {'object_name': 'Language'},
            'code': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '4'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'Teller.tale': {
            'Meta': {'object_name': 'Tale'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['Teller.Language']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '150'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tales'", 'to': u"orm['Teller.User']"})
        },
        u'Teller.talelink': {
            'Meta': {'object_name': 'TaleLink'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'entrances'", 'null': 'True', 'to': u"orm['Teller.TalePart']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'choices'", 'to': u"orm['Teller.TalePart']"})
        },
        u'Teller.talepart': {
            'Meta': {'object_name': 'TalePart'},
            'content': ('ckeditor.fields.RichTextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'poll_end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '150'}),
            'tale': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['Teller.Tale']"})
        },
        u'Teller.user': {
            'Meta': {'object_name': 'User'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'selected_links': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['Teller.TaleLink']", 'symmetrical': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '150'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '25'})
        }
    }

    complete_apps = ['Teller']