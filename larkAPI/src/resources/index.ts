import type * as lark from "@larksuiteoapi/node-sdk";
import { normalizeLarkApiError } from "../errors";

type SdkMethod = (...args: any[]) => Promise<unknown>;
type PayloadOf<T extends SdkMethod> = NonNullable<Parameters<T>[0]>;

/**
 * Preserve the official SDK request and response types while keeping its
 * internal request-options type out of this library's public method signatures.
 */
function safe<T extends SdkMethod>(
  operation: string,
  method: T,
): (payload: PayloadOf<T>) => Promise<Awaited<ReturnType<T>>> {
  return async (payload) => {
    try {
      return (await method(payload)) as Awaited<ReturnType<T>>;
    } catch (error) {
      throw normalizeLarkApiError(error, operation);
    }
  };
}

/**
 * Named, grouped Bitable API methods exposed by the official SDK generated
 * client. Request and response types are inferred from the pinned SDK declarations.
 * API_COVERAGE.md tracks endpoint inventory and verification state.
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
      create: safe("bitable.appTableRecord.create", b.appTableRecord.create),
      get: safe("bitable.appTableRecord.get", b.appTableRecord.get),
      list: safe("bitable.appTableRecord.list", b.appTableRecord.list),
      search: safe("bitable.appTableRecord.search", b.appTableRecord.search),
      update: safe("bitable.appTableRecord.update", b.appTableRecord.update),
      delete: safe("bitable.appTableRecord.delete", b.appTableRecord.delete),
      batchCreate: safe("bitable.appTableRecord.batchCreate", b.appTableRecord.batchCreate),
      batchGet: safe("bitable.appTableRecord.batchGet", b.appTableRecord.batchGet),
      batchUpdate: safe("bitable.appTableRecord.batchUpdate", b.appTableRecord.batchUpdate),
      batchDelete: safe("bitable.appTableRecord.batchDelete", b.appTableRecord.batchDelete),
    },
    fields: {
      create: safe("bitable.appTableField.create", b.appTableField.create),
      list: safe("bitable.appTableField.list", b.appTableField.list),
      update: safe("bitable.appTableField.update", b.appTableField.update),
      delete: safe("bitable.appTableField.delete", b.appTableField.delete),
    },
    views: {
      create: safe("bitable.appTableView.create", b.appTableView.create),
      get: safe("bitable.appTableView.get", b.appTableView.get),
      list: safe("bitable.appTableView.list", b.appTableView.list),
      update: safe("bitable.appTableView.patch", b.appTableView.patch),
      delete: safe("bitable.appTableView.delete", b.appTableView.delete),
    },
    forms: {
      get: safe("bitable.appTableForm.get", b.appTableForm.get),
      update: safe("bitable.appTableForm.patch", b.appTableForm.patch),
      upgrade: safe("bitable.appTableForm.upgrade", b.appTableForm.upgrade),
      listFields: safe("bitable.appTableFormField.list", b.appTableFormField.list),
      updateField: safe("bitable.appTableFormField.patch", b.appTableFormField.patch),
    },
    fieldGroups: {
      create: safe("bitable.appTableFieldGroup.create", b.appTableFieldGroup.create),
    },
    dashboards: {
      list: safe("bitable.appDashboard.list", b.appDashboard.list),
      copy: safe("bitable.appDashboard.copy", b.appDashboard.copy),
    },
    roles: {
      create: safe("bitable.appRole.create", b.appRole.create),
      list: safe("bitable.appRole.list", b.appRole.list),
      update: safe("bitable.appRole.update", b.appRole.update),
      delete: safe("bitable.appRole.delete", b.appRole.delete),
      listMembers: safe("bitable.appRoleMember.list", b.appRoleMember.list),
      createMember: safe("bitable.appRoleMember.create", b.appRoleMember.create),
      batchCreateMembers: safe("bitable.appRoleMember.batchCreate", b.appRoleMember.batchCreate),
      deleteMember: safe("bitable.appRoleMember.delete", b.appRoleMember.delete),
      batchDeleteMembers: safe("bitable.appRoleMember.batchDelete", b.appRoleMember.batchDelete),
    },
    workflows: {
      list: safe("bitable.appWorkflow.list", b.appWorkflow.list),
      update: safe("bitable.appWorkflow.update", b.appWorkflow.update),
    },
    blockWorkflows: {
      list: safe("bitable.appBlockWorkflow.list", b.appBlockWorkflow.list),
    },
  };
}
