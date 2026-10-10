import type * as lark from "@larksuiteoapi/node-sdk";
import { normalizeLarkApiError } from "../errors";

type AsyncMethod = (...args: any[]) => Promise<any>;

function safe<T extends AsyncMethod>(operation: string, method: T): T {
  return (async (...args: Parameters<T>) => {
    try {
      return await method(...args);
    } catch (error) {
      throw normalizeLarkApiError(error, operation);
    }
  }) as T;
}

/**
 * Named, grouped Bitable API methods exposed by the official Node SDK's
 * generated Bitable client. This is the SDK-backed method surface currently
 * inventoried for this package; API_COVERAGE.md tracks gaps and verification.
 */
export function createBitableMethods(client: lark.Client) {
  const b = client.bitable;

  return {
    apps: {
      create: safe("bitable.app.create", b.app.create),
      get: safe("bitable.app.get", b.app.get),
      update: safe("bitable.app.update", b.app.update),
      copy: safe("bitable.app.copy", b.app.copy),
    },
    tables: {
      create: safe("bitable.appTable.create", b.appTable.create),
      list: safe("bitable.appTable.list", b.appTable.list),
      update: safe("bitable.appTable.patch", b.appTable.patch),
      delete: safe("bitable.appTable.delete", b.appTable.delete),
      batchCreate: safe("bitable.appTable.batchCreate", b.appTable.batchCreate),
      batchDelete: safe("bitable.appTable.batchDelete", b.appTable.batchDelete),
    },
    records: {
      create: safe("bitable.appTable.record.create", b.appTable.record.create),
      get: safe("bitable.appTable.record.get", b.appTable.record.get),
      list: safe("bitable.appTable.record.list", b.appTable.record.list),
      search: safe("bitable.appTable.record.search", b.appTable.record.search),
      update: safe("bitable.appTable.record.update", b.appTable.record.update),
      delete: safe("bitable.appTable.record.delete", b.appTable.record.delete),
      batchCreate: safe("bitable.appTable.record.batchCreate", b.appTable.record.batchCreate),
      batchGet: safe("bitable.appTable.record.batchGet", b.appTable.record.batchGet),
      batchUpdate: safe("bitable.appTable.record.batchUpdate", b.appTable.record.batchUpdate),
      batchDelete: safe("bitable.appTable.record.batchDelete", b.appTable.record.batchDelete),
    },
    fields: {
      create: safe("bitable.appTable.field.create", b.appTable.field.create),
      list: safe("bitable.appTable.field.list", b.appTable.field.list),
      update: safe("bitable.appTable.field.update", b.appTable.field.update),
      delete: safe("bitable.appTable.field.delete", b.appTable.field.delete),
    },
    views: {
      create: safe("bitable.appTable.view.create", b.appTable.view.create),
      get: safe("bitable.appTable.view.get", b.appTable.view.get),
      list: safe("bitable.appTable.view.list", b.appTable.view.list),
      update: safe("bitable.appTable.view.patch", b.appTable.view.patch),
      delete: safe("bitable.appTable.view.delete", b.appTable.view.delete),
    },
    forms: {
      get: safe("bitable.appTable.form.get", b.appTable.form.get),
      update: safe("bitable.appTable.form.patch", b.appTable.form.patch),
      upgrade: safe("bitable.appTable.form.upgrade", b.appTable.form.upgrade),
      listFields: safe("bitable.appTable.form.field.list", b.appTable.form.field.list),
      updateField: safe("bitable.appTable.form.field.patch", b.appTable.form.field.patch),
    },
    fieldGroups: {
      create: safe("bitable.appTable.fieldGroup.create", b.appTable.fieldGroup.create),
    },
    dashboards: {
      list: safe("bitable.appDashboard.list", b.appDashboard.list),
      copy: safe("bitable.appDashboard.copy", b.appDashboard.copy),
    },
    roles: {
      create: safe("bitable.app.role.create", b.app.role.create),
      list: safe("bitable.app.role.list", b.app.role.list),
      update: safe("bitable.app.role.update", b.app.role.update),
      delete: safe("bitable.app.role.delete", b.app.role.delete),
      listMembers: safe("bitable.app.role.member.list", b.app.role.member.list),
      createMember: safe("bitable.app.role.member.create", b.app.role.member.create),
      batchCreateMembers: safe("bitable.app.role.member.batchCreate", b.app.role.member.batchCreate),
      deleteMember: safe("bitable.app.role.member.delete", b.app.role.member.delete),
      batchDeleteMembers: safe("bitable.app.role.member.batchDelete", b.app.role.member.batchDelete),
    },
    workflows: {
      list: safe("bitable.app.workflow.list", b.app.workflow.list),
      update: safe("bitable.app.workflow.update", b.app.workflow.update),
    },
    blockWorkflows: {
      list: safe("bitable.app.blockWorkflow.list", b.app.blockWorkflow.list),
    },
  };
}

export type BitableMethods = ReturnType<typeof createBitableMethods>;
