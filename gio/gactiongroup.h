/*
 * Copyright © 2010 Codethink Limited
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published
 * by the Free Software Foundation; either version 2 of the licence or (at
 * your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General
 * Public License along with this library; if not, write to the
 * Free Software Foundation, Inc., 59 Temple Place, Suite 330,
 * Boston, MA 02111-1307, USA.
 *
 * Authors: Ryan Lortie <desrt@desrt.ca>
 */

#if !defined (__GIO_GIO_H_INSIDE__) && !defined (GIO_COMPILATION)
#error "Only <gio/gio.h> can be included directly."
#endif

#ifndef __G_ACTION_GROUP_H__
#define __G_ACTION_GROUP_H__

#include <gio/giotypes.h>

G_BEGIN_DECLS

#define G_TYPE_ACTION_GROUP                                 (g_action_group_get_type ())
#define G_ACTION_GROUP(inst)                                (G_TYPE_CHECK_INSTANCE_CAST ((inst),                     \
                                                             G_TYPE_ACTION_GROUP, GActionGroup))
#define G_ACTION_GROUP_CLASS(class)                         (G_TYPE_CHECK_CLASS_CAST ((class),                       \
                                                             G_TYPE_ACTION_GROUP, GActionGroupClass))
#define G_IS_ACTION_GROUP(inst)                             (G_TYPE_CHECK_INSTANCE_TYPE ((inst), G_TYPE_ACTION_GROUP))
#define G_IS_ACTION_GROUP_CLASS(class)                      (G_TYPE_CHECK_CLASS_TYPE ((class), G_TYPE_ACTION_GROUP))
#define G_ACTION_GROUP_GET_CLASS(inst)                      (G_TYPE_INSTANCE_GET_CLASS ((inst),                      \
                                                             G_TYPE_ACTION_GROUP, GActionGroupClass))

typedef struct _GActionGroupPrivate                         GActionGroupPrivate;
typedef struct _GActionGroupClass                           GActionGroupClass;

/**
 * GActionGroup:
 *
 * The #GActionGroup structure contains private data and should only be accessed using the provided API.
 *
 * Since: 2.26
 */
struct _GActionGroup
{
  /*< private >*/
  GObject parent_instance;

  GActionGroupPrivate *priv;
};

/**
 * GActionGroupClass:
 * @has_action: the virtual function pointer for g_action_group_has_action()
 * @list_actions: the virtual function pointer for g_action_group_list_actions()
 * @get_parameter_type: the virtual function pointer for g_action_group_get_parameter_type()
 * @get_state_type: the virtual function pointer for g_action_group_get_state_type()
 * @get_state_hint: the virtual function pointer for g_action_group_get_state_hint()
 * @get_enabled: the virtual function pointer for g_action_group_get_enabled()
 * @get_state: the virtual function pointer for g_action_group_get_state()
 * @set_state: the virtual function pointer for g_action_group_set_state()
 * @activate: the virtual function pointer for g_action_group_activate()
 * @action_added: the class closure for the action-added signal
 * @action_removed: the class closure for the action-removed signal
 * @action_enabled_changed: the class closure for the action-enabled-changed signal
 * @action_state_changed: the class closure for the action-enabled-changed signal
 *
 * The virtual function table for #GActionGroup.
 *
 * Since: 2.26
 */
struct _GActionGroupClass
{
  /*< private >*/
  GObjectClass parent_class;

  /*< public >*/
  /* virtual functions */
  gboolean              (* has_action)              (GActionGroup  *action_group,
                                                     const gchar   *action_name);

  gchar **              (* list_actions)            (GActionGroup  *action_group);

  gboolean              (* get_enabled)             (GActionGroup  *action_group,
                                                     const gchar   *action_name);

  const GVariantType *  (* get_parameter_type)      (GActionGroup  *action_group,
                                                     const gchar   *action_name);

  const GVariantType *  (* get_state_type)          (GActionGroup  *action_group,
                                                     const gchar   *action_name);

  GVariant *            (* get_state_hint)          (GActionGroup  *action_group,
                                                     const gchar   *action_name);

  GVariant *            (* get_state)               (GActionGroup  *action_group,
                                                     const gchar   *action_name);

  void                  (* set_state)               (GActionGroup  *action_group,
                                                     const gchar   *action_name,
                                                     GVariant      *value);

  void                  (* activate)                (GActionGroup  *action_group,
                                                     const gchar   *action_name,
                                                     GVariant      *parameter);

  /*< private >*/
  gpointer vtable_padding[6];

  /*< public >*/
  /* signals */
  void                  (* action_added)            (GActionGroup  *action_group,
                                                     const gchar   *action_name);
  void                  (* action_removed)          (GActionGroup  *action_group,
                                                     const gchar   *action_name);
  void                  (* action_enabled_changed)  (GActionGroup  *action_group,
                                                     const gchar   *action_name,
                                                     gboolean       enabled);
  void                  (* action_state_changed)    (GActionGroup   *action_group,
                                                     const gchar    *action_name,
                                                     GVariant       *value);

  /*< private >*/
  gpointer signal_padding[6];
};

GType                   g_action_group_get_type                         (void) G_GNUC_CONST;

gboolean                g_action_group_has_action                       (GActionGroup *action_group,
                                                                         const gchar  *action_name);
gchar **                g_action_group_list_actions                     (GActionGroup *action_group);

const GVariantType *    g_action_group_get_parameter_type               (GActionGroup *action_group,
                                                                         const gchar  *action_name);
const GVariantType *    g_action_group_get_state_type                   (GActionGroup *action_group,
                                                                         const gchar  *action_name);
GVariant *              g_action_group_get_state_hint                   (GActionGroup *action_group,
                                                                         const gchar  *action_name);

gboolean                g_action_group_get_enabled                      (GActionGroup *action_group,
                                                                         const gchar  *action_name);

GVariant *              g_action_group_get_state                        (GActionGroup *action_group,
                                                                         const gchar  *action_name);
void                    g_action_group_set_state                        (GActionGroup *action_group,
                                                                         const gchar  *action_name,
                                                                         GVariant     *value);

void                    g_action_group_activate                         (GActionGroup *action_group,
                                                                         const gchar  *action_name,
                                                                         GVariant     *parameter);

/* signals */
void                    g_action_group_action_added                     (GActionGroup *action_group,
                                                                         const gchar  *action_name);
void                    g_action_group_action_removed                   (GActionGroup *action_group,
                                                                         const gchar  *action_name);
void                    g_action_group_action_enabled_changed           (GActionGroup *action_group,
                                                                         const gchar  *action_name,
                                                                         gboolean      enabled);

void                    g_action_group_action_state_changed             (GActionGroup *action_group,
                                                                         const gchar  *action_name,
                                                                         GVariant     *state);

G_END_DECLS

#endif /* __G_ACTION_GROUP_H__ */