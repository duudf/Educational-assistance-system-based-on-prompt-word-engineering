<template>
  <assignment-detail :is-edit="true" />
</template>
<script>
import AssignmentDetail from './components/AssignmentDetail'
export default {
  name: 'EditAssignment',
  components: { AssignmentDetail }
}
</script>
